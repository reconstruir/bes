#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
import queue
import threading
import time
from os import path

from bes.files.bf_file_ops import bf_file_ops
from bes.files.bf_filename import bf_filename
from bes.files.checksum.bf_checksum import bf_checksum
from bes.system.log import log

from .bf_file_mover_status import bf_file_mover_status

class bf_file_mover_worker:

  def __init__(self, database, options):
    self._database = database
    self._options = options
    self._queue = queue.Queue()
    self._stop_event = threading.Event()
    self._thread = None

  def is_running(self):
    return self._thread is not None and self._thread.is_alive()

  def start(self):
    self._stop_event.clear()
    self._thread = threading.Thread(
      target=self._run,
      daemon=True,
      name='bf_file_mover_worker'
    )
    self._thread.start()

  def stop(self, wait=True):
    self._stop_event.set()
    if wait and self._thread is not None:
      self._thread.join()

  def enqueue(self, operation_id):
    self._queue.put(operation_id)

  def _run(self):
    while not self._stop_event.is_set():
      try:
        operation_id = self._queue.get(timeout=0.1)
      except queue.Empty:
        continue
      try:
        self._process(operation_id)
      except Exception as ex:
        log.log_w('bf_file_mover_worker', f'Unhandled error processing {operation_id}: {ex}')
        try:
          self._database.update_status(
            operation_id,
            bf_file_mover_status.failed,
            completed_at=int(time.time()),
            error_message=str(ex)
          )
        except Exception:
          pass
      finally:
        self._queue.task_done()

  def _process(self, operation_id):
    operation = self._database.get_operation(operation_id)
    if operation is None:
      return

    dst_dir = path.dirname(operation.destination_path)
    if not self._destination_reachable(dst_dir):
      self._database.update_status(
        operation_id,
        bf_file_mover_status.paused,
        paused_at=int(time.time())
      )
      if self._options.on_pause:
        self._options.on_pause(operation)
      return

    if path.exists(operation.destination_path):
      if bf_file_ops.files_are_the_same(operation.staging_path, operation.destination_path):
        os.remove(operation.staging_path)
        staging_uuid_dir = path.dirname(operation.staging_path)
        try:
          os.rmdir(staging_uuid_dir)
        except OSError:
          pass
        self._database.update_status(
          operation_id,
          bf_file_mover_status.done,
          completed_at=int(time.time())
        )
        if self._options.on_complete:
          self._options.on_complete(operation)
        return

    self._database.update_status(
      operation_id,
      bf_file_mover_status.copying,
      copy_started_at=int(time.time())
    )

    try:
      self._execute_move(operation)
      self._database.update_status(
        operation_id,
        bf_file_mover_status.done,
        completed_at=int(time.time())
      )
      if self._options.on_complete:
        self._options.on_complete(operation)
    except Exception as ex:
      self._database.update_status(
        operation_id,
        bf_file_mover_status.failed,
        completed_at=int(time.time()),
        error_message=str(ex)
      )
      raise

  def _execute_move(self, operation):
    staging_path = operation.staging_path
    destination_path = operation.destination_path
    staging_uuid_dir = path.dirname(staging_path)

    dst_dir = path.dirname(destination_path)
    os.makedirs(dst_dir, exist_ok=True)

    destination_path = self._make_unique_destination(destination_path, operation.operation_id)

    if self._same_device(staging_path, dst_dir):
      os.rename(staging_path, destination_path)
    else:
      self._cross_device_copy(staging_path, destination_path, operation)

    try:
      os.rmdir(staging_uuid_dir)
    except OSError:
      pass

  def _cross_device_copy(self, staging_path, destination_path, operation):
    dst_dir = path.dirname(destination_path)
    tmp_path = path.join(dst_dir, f'{operation.operation_id}.tmp')
    expected_size = os.stat(staging_path).st_size
    min_interval = self._options.progress_min_interval if self._options.progress_min_interval is not None else 0.1
    last_progress_time = 0.0
    last_reported_percent = -1
    try:
      with open(staging_path, 'rb') as source_file:
        with open(tmp_path, 'wb') as destination_file:
          bytes_copied = 0
          while True:
            chunk = source_file.read(self._options.chunk_size)
            if not chunk:
              break
            destination_file.write(chunk)
            bytes_copied += len(chunk)
            if self._options.on_progress:
              is_last = (bytes_copied == expected_size)
              current_percent = int(bytes_copied * 100 / expected_size) if expected_size > 0 else 100
              now = time.monotonic()
              if is_last or (current_percent > last_reported_percent and now - last_progress_time >= min_interval):
                self._options.on_progress(operation, bytes_copied, expected_size)
                last_progress_time = now
                last_reported_percent = current_percent
          destination_file.flush()
          os.fsync(destination_file.fileno())
    except Exception:
      if path.exists(tmp_path):
        os.remove(tmp_path)
      raise

    actual_size = os.stat(tmp_path).st_size
    if actual_size != expected_size:
      os.remove(tmp_path)
      raise RuntimeError(
        f'Size mismatch after copy: expected {expected_size}, got {actual_size}'
      )

    if self._options.verify_checksum_after_copy:
      source_checksum = bf_checksum.checksum(staging_path, 'sha256')
      tmp_checksum = bf_checksum.checksum(tmp_path, 'sha256')
      if source_checksum != tmp_checksum:
        os.remove(tmp_path)
        raise RuntimeError('Checksum mismatch after copy')

    os.rename(tmp_path, destination_path)
    os.remove(staging_path)

  def _destination_reachable(self, directory):
    try:
      return path.isdir(directory)
    except OSError:
      return False

  def _same_device(self, source_path, destination_dir):
    return os.stat(source_path).st_dev == os.stat(destination_dir).st_dev


  @staticmethod
  def _make_unique_destination(destination_path, operation_id):
    if not path.exists(destination_path):
      return destination_path
    directory = path.dirname(destination_path)
    basename = path.basename(destination_path)
    stem = bf_filename.without_extension(basename)
    ext = bf_filename.extension(basename)
    new_stem = f'{stem}-{operation_id[:8]}'
    new_basename = bf_filename.add_extension(new_stem, ext)
    return path.join(directory, new_basename)

#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import hashlib
import os
import time
import uuid
from os import path

from bes.files.core.bf_volume_locator import bf_volume_locator
from bes.system.check import check
from bes.system.filesystem import filesystem
from bes.system.host import host
from bes.system.log import log

from .bf_file_mover_database import bf_file_mover_database
from .bf_file_mover_move_result import bf_file_mover_move_result
from .bf_file_mover_move_status import bf_file_mover_move_status
from .bf_file_mover_operation import bf_file_mover_operation
from .bf_file_mover_options import bf_file_mover_options
from .bf_file_mover_restore_result import bf_file_mover_restore_result
from .bf_file_mover_restore_status import bf_file_mover_restore_status
from .bf_file_mover_status import bf_file_mover_status
from .bf_file_mover_worker import bf_file_mover_worker

class bf_file_mover:

  _PATH_MAX_MACOS = 1024
  _PATH_MAX_LINUX = 4096

  def __init__(self, database_path, options=None):
    check.check_string(database_path)

    self._database_path = database_path
    self._options = options or bf_file_mover_options()
    self._database = bf_file_mover_database(database_path)
    self._worker = None

  def start_worker(self):
    if self._worker is not None and self._worker.is_running():
      raise RuntimeError('Worker is already running')
    self._worker = bf_file_mover_worker(self._database, self._options)
    self._run_startup_recovery()
    self._worker.start()

  def stop_worker(self, wait=True):
    if self._worker is None:
      return
    self._worker.stop(wait=wait)
    self._worker = None

  def move(self, source_path, destination_path):
    check.check_string(source_path)
    check.check_string(destination_path)

    if self._worker is None or not self._worker.is_running():
      raise RuntimeError('Worker is not running; call start_worker() first')

    source_path = path.abspath(source_path)
    destination_path = path.abspath(destination_path)

    if path.basename(source_path) != path.basename(destination_path):
      raise ValueError(
        f'Source and destination must have the same basename: '
        f'{path.basename(source_path)!r} != {path.basename(destination_path)!r}'
      )

    path_max = self._PATH_MAX_MACOS if host.is_macos() else self._PATH_MAX_LINUX
    if len(destination_path.encode('utf-8')) >= path_max:
      raise ValueError(
        f'Destination path exceeds PATH_MAX ({path_max}): {destination_path}'
      )

    destination_dir = path.dirname(destination_path)
    if path.isdir(destination_dir):
      source_device = os.stat(source_path).st_dev
      destination_device = os.stat(destination_dir).st_dev
      if source_device != destination_device:
        source_size = os.stat(source_path).st_size
        in_flight = self._in_flight_bytes_for_device(destination_dir)
        if source_size + in_flight > filesystem.free_disk_space(destination_dir):
          return bf_file_mover_move_result(bf_file_mover_move_status.no_space)

    db_scope = hashlib.sha256(self._database_path.encode()).hexdigest()[:16]
    if self._options.staging_root is not None:
      staging_dir = path.join(self._options.staging_root, db_scope)
    else:
      staging_dir = bf_volume_locator.directory_for_file(source_path, f'move_staging/{db_scope}')
    operation_id = str(uuid.uuid4())
    staging_uuid_dir = path.join(staging_dir, operation_id)
    os.makedirs(staging_uuid_dir)
    staging_path = path.join(staging_uuid_dir, path.basename(source_path))

    destination_device_id = None
    if path.isdir(destination_dir):
      destination_device_id = str(os.stat(destination_dir).st_dev)

    try:
      os.rename(source_path, staging_path)
    except Exception as ex:
      os.rmdir(staging_uuid_dir)
      raise

    now = int(time.time())
    operation = bf_file_mover_operation(
      operation_id=operation_id,
      source_path=source_path,
      staging_path=staging_path,
      destination_path=destination_path,
      destination_device_id=destination_device_id,
      status=bf_file_mover_status.staging_done,
      submitted_at=now,
      staged_at=now,
    )
    self._database.insert_operation(operation)
    self._worker.enqueue(operation_id)

    return bf_file_mover_move_result(bf_file_mover_move_status.success, operation_id=operation_id)

  def status(self, operation_id):
    check.check_string(operation_id)

    operation = self._database.get_operation(operation_id)
    if operation is None:
      raise KeyError(f'Unknown operation: {operation_id}')
    return operation.status

  def operation(self, operation_id):
    check.check_string(operation_id)

    return self._database.get_operation(operation_id)

  def list_operations(self, status=None, since=None):
    return self._database.list_operations(status=status, since=since)

  def resume_paused(self):
    if self._worker is None or not self._worker.is_running():
      raise RuntimeError('Worker is not running; call start_worker() first')
    self._requeue_reachable_paused()

  def list_orphans(self):
    all_operations = self._database.list_operations()
    all_operation_ids = {operation.operation_id for operation in all_operations}
    staging_roots = {
      path.dirname(path.dirname(operation.staging_path))
      for operation in all_operations
    }

    orphans = []
    for staging_root in staging_roots:
      if not path.isdir(staging_root):
        continue
      for entry_name in os.listdir(staging_root):
        entry_path = path.join(staging_root, entry_name)
        if not path.isdir(entry_path):
          continue
        if entry_name not in all_operation_ids:
          for filename in os.listdir(entry_path):
            orphans.append(path.join(entry_path, filename))

    return orphans

  def retry(self, operation_id):
    check.check_string(operation_id)

    if self._worker is None or not self._worker.is_running():
      raise RuntimeError('Worker is not running; call start_worker() first')

    operation = self._database.get_operation(operation_id)
    if operation is None:
      raise KeyError(f'Unknown operation: {operation_id}')
    if operation.status == bf_file_mover_status.expired:
      raise RuntimeError(f'Operation {operation_id} is expired and cannot be retried')
    if operation.status != bf_file_mover_status.failed:
      raise RuntimeError(
        f'Operation {operation_id} is not in failed state (status: {operation.status.value})'
      )
    if not path.exists(operation.staging_path):
      raise RuntimeError(
        f'Staging file missing for operation {operation_id}: {operation.staging_path}'
      )

    self._database.update_status(operation_id, bf_file_mover_status.staging_done)
    self._worker.enqueue(operation_id)

  def vacuum_staging(self, minimum_age_days):
    check.check_int(minimum_age_days)

    cutoff = int(time.time()) - minimum_age_days * 86400

    to_expire = []

    for operation in self._database.list_operations(status=bf_file_mover_status.failed):
      age_timestamp = operation.completed_at or operation.staged_at or operation.submitted_at
      if age_timestamp is not None and age_timestamp < cutoff:
        to_expire.append(operation)

    for operation in self._database.list_operations(status=bf_file_mover_status.paused):
      if not path.exists(operation.staging_path):
        to_expire.append(operation)

    now = int(time.time())
    for operation in to_expire:
      if path.exists(operation.staging_path):
        os.remove(operation.staging_path)
      staging_uuid_dir = path.dirname(operation.staging_path)
      if path.isdir(staging_uuid_dir):
        try:
          os.rmdir(staging_uuid_dir)
        except OSError:
          pass
      self._database.update_status(
        operation.operation_id,
        bf_file_mover_status.expired,
        completed_at=now
      )

  def restore(self, operation_id):
    check.check_string(operation_id)

    operation = self._database.get_operation(operation_id)
    if operation is None:
      raise KeyError(f'Unknown operation: {operation_id}')

    restorable = (bf_file_mover_status.failed, bf_file_mover_status.paused)
    if operation.status not in restorable:
      return bf_file_mover_restore_result(bf_file_mover_restore_status.wrong_status, operation_id=operation_id)

    if not path.exists(operation.staging_path):
      return bf_file_mover_restore_result(bf_file_mover_restore_status.staging_file_missing, operation_id=operation_id)

    source_dir = path.dirname(operation.source_path)
    if not path.isdir(source_dir):
      return bf_file_mover_restore_result(bf_file_mover_restore_status.source_directory_missing, operation_id=operation_id)

    if path.exists(operation.source_path):
      return bf_file_mover_restore_result(bf_file_mover_restore_status.source_path_occupied, operation_id=operation_id)

    os.rename(operation.staging_path, operation.source_path)

    staging_uuid_dir = path.dirname(operation.staging_path)
    try:
      os.rmdir(staging_uuid_dir)
    except OSError:
      pass

    self._database.update_status(operation_id, bf_file_mover_status.restored, completed_at=int(time.time()))
    return bf_file_mover_restore_result(bf_file_mover_restore_status.success, operation_id=operation_id)

  def _in_flight_bytes_for_device(self, destination_dir):
    try:
      destination_device = os.stat(destination_dir).st_dev
    except OSError:
      return 0
    total = 0
    for status in (bf_file_mover_status.staging_done, bf_file_mover_status.copying):
      for operation in self._database.list_operations(status=status):
        op_dst_dir = path.dirname(operation.destination_path)
        try:
          if os.stat(op_dst_dir).st_dev != destination_device:
            continue
          staging_stat = os.stat(operation.staging_path)
          if staging_stat.st_dev == destination_device:
            continue
          total += staging_stat.st_size
        except OSError:
          pass
    return total

  def _run_startup_recovery(self):
    for operation in self._database.list_operations(status=bf_file_mover_status.copying):
      if path.exists(operation.staging_path):
        self._database.update_status(operation.operation_id, bf_file_mover_status.staging_done)
        self._worker.enqueue(operation.operation_id)
      else:
        self._database.update_status(
          operation.operation_id,
          bf_file_mover_status.failed,
          completed_at=int(time.time()),
          error_message='Staging file missing at startup recovery'
        )
        staging_uuid_dir = path.dirname(operation.staging_path)
        if path.isdir(staging_uuid_dir):
          try:
            os.rmdir(staging_uuid_dir)
          except OSError:
            pass

    self._requeue_reachable_paused()
    self._warn_orphans()

  def _requeue_reachable_paused(self):
    for operation in self._database.list_operations(status=bf_file_mover_status.paused):
      destination_dir = path.dirname(operation.destination_path)
      if path.isdir(destination_dir):
        self._database.update_status(operation.operation_id, bf_file_mover_status.staging_done)
        self._worker.enqueue(operation.operation_id)

  def _warn_orphans(self):
    for orphan_path in self.list_orphans():
      try:
        size = os.stat(orphan_path).st_size
        log.log_w(
          'bf_file_mover',
          f'Orphaned staging file: {orphan_path} ({size} bytes, no database record)'
        )
      except OSError:
        log.log_w('bf_file_mover', f'Orphaned staging file: {orphan_path} (no database record)')

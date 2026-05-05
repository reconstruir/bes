#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
import time
import threading
import unittest
from os import path
from unittest import mock

from bes.testing.unit_test import unit_test
from bes.files.move.bf_file_mover import bf_file_mover
from bes.files.move.bf_file_mover_database import bf_file_mover_database
from bes.files.move.bf_file_mover_operation import bf_file_mover_operation
from bes.files.move.bf_file_mover_options import bf_file_mover_options
from bes.files.move.bf_file_mover_status import bf_file_mover_status

class test_bf_file_mover(unit_test):

  def _make_mover(self, options=None):
    database_path = path.join(self.make_temp_dir(), 'test_move.sqlite')
    return bf_file_mover(database_path, options)

  def _make_source_file(self, content='hello', filename='foo.flac'):
    tmp_dir = self.make_temp_dir()
    filepath = path.join(tmp_dir, filename)
    with open(filepath, 'wb') as f:
      f.write(content.encode('utf-8'))
    return filepath

  def _wait_for_status(self, mover, operation_id, expected_status, timeout=5.0):
    deadline = time.time() + timeout
    while time.time() < deadline:
      current = mover.status(operation_id)
      if current == expected_status:
        return True
      if current in (bf_file_mover_status.failed, bf_file_mover_status.done):
        if current != expected_status:
          return False
      time.sleep(0.05)
    return False

  # constructor

  def test_init_creates_database_file(self):
    tmp_dir = self.make_temp_dir()
    database_path = path.join(tmp_dir, 'move.sqlite')
    bf_file_mover(database_path)
    self.assertTrue(path.exists(database_path))

  def test_init_creates_database_parent_dirs(self):
    tmp_dir = self.make_temp_dir()
    database_path = path.join(tmp_dir, 'sub', 'nested', 'move.sqlite')
    bf_file_mover(database_path)
    self.assertTrue(path.exists(database_path))

  # worker lifecycle

  def test_start_worker_starts_thread(self):
    mover = self._make_mover()
    mover.start_worker()
    self.assertTrue(mover._worker.is_running())
    mover.stop_worker()

  def test_stop_worker(self):
    mover = self._make_mover()
    mover.start_worker()
    mover.stop_worker(wait=True)
    self.assertIsNone(mover._worker)

  def test_double_start_raises(self):
    mover = self._make_mover()
    mover.start_worker()
    with self.assertRaises(RuntimeError):
      mover.start_worker()
    mover.stop_worker()

  def test_move_raises_if_worker_not_running(self):
    mover = self._make_mover()
    src = self._make_source_file()
    dst = path.join(self.make_temp_dir(), 'foo.flac')
    with self.assertRaises(RuntimeError):
      mover.move(src, dst)

  # validation

  def test_move_raises_on_mismatched_basename(self):
    mover = self._make_mover()
    mover.start_worker()
    src = self._make_source_file(filename='foo.flac')
    dst = path.join(self.make_temp_dir(), 'bar.flac')
    with self.assertRaises(ValueError):
      mover.move(src, dst)
    mover.stop_worker()

  def test_move_raises_on_mismatched_basename_source_untouched(self):
    mover = self._make_mover()
    mover.start_worker()
    src = self._make_source_file(filename='foo.flac')
    dst = path.join(self.make_temp_dir(), 'bar.flac')
    with self.assertRaises(ValueError):
      mover.move(src, dst)
    self.assertTrue(path.exists(src))
    mover.stop_worker()

  def test_move_raises_on_destination_path_too_long(self):
    mover = self._make_mover()
    mover.start_worker()
    src = self._make_source_file(filename='foo.flac')
    long_path = path.join(self.make_temp_dir(), 'x' * 5000, 'foo.flac')
    with self.assertRaises(ValueError):
      mover.move(src, long_path)
    mover.stop_worker()

  def test_move_raises_on_destination_path_too_long_source_untouched(self):
    mover = self._make_mover()
    mover.start_worker()
    src = self._make_source_file(filename='foo.flac')
    long_path = path.join(self.make_temp_dir(), 'x' * 5000, 'foo.flac')
    with self.assertRaises(ValueError):
      mover.move(src, long_path)
    self.assertTrue(path.exists(src))
    mover.stop_worker()

  # staging

  def test_move_stages_file_immediately(self):
    mover = self._make_mover()
    mover.start_worker()
    src = self._make_source_file()
    dst_dir = self.make_temp_dir()
    dst = path.join(dst_dir, 'foo.flac')
    operation_id = mover.move(src, dst)
    self.assertFalse(path.exists(src))
    mover.stop_worker()

  def test_move_creates_uuid_directory(self):
    mover = self._make_mover()
    mover.start_worker()
    src = self._make_source_file()
    dst_dir = self.make_temp_dir()
    dst = path.join(dst_dir, 'foo.flac')
    operation_id = mover.move(src, dst)
    operation = mover.operation(operation_id)
    staging_uuid_dir = path.dirname(operation.staging_path)
    self.assertTrue(path.isdir(staging_uuid_dir) or path.exists(dst))
    mover.stop_worker()

  def test_staging_preserves_basename(self):
    mover = self._make_mover()
    mover.start_worker()
    src = self._make_source_file(filename='myfile.flac')
    dst_dir = self.make_temp_dir()
    dst = path.join(dst_dir, 'myfile.flac')
    operation_id = mover.move(src, dst)
    operation = mover.operation(operation_id)
    self.assertEqual('myfile.flac', path.basename(operation.staging_path))
    mover.stop_worker()

  def test_two_same_basename_files_no_collision(self):
    mover = self._make_mover()
    mover.start_worker()
    src1 = self._make_source_file(content='file1', filename='track.flac')
    src2 = self._make_source_file(content='file2', filename='track.flac')
    dst_dir = self.make_temp_dir()
    os.makedirs(path.join(dst_dir, 'sub1'))
    os.makedirs(path.join(dst_dir, 'sub2'))
    dst1 = path.join(dst_dir, 'sub1', 'track.flac')
    dst2 = path.join(dst_dir, 'sub2', 'track.flac')
    op1 = mover.move(src1, dst1)
    op2 = mover.move(src2, dst2)
    self.assertNotEqual(mover.operation(op1).staging_path, mover.operation(op2).staging_path)
    self.assertTrue(self._wait_for_status(mover, op1, bf_file_mover_status.done))
    self.assertTrue(self._wait_for_status(mover, op2, bf_file_mover_status.done))
    self.assertEqual(b'file1', open(dst1, 'rb').read())
    self.assertEqual(b'file2', open(dst2, 'rb').read())
    mover.stop_worker()

  # same-device move

  def test_move_same_device_completes(self):
    mover = self._make_mover()
    mover.start_worker()
    src = self._make_source_file(content='test content')
    dst_dir = self.make_temp_dir()
    dst = path.join(dst_dir, 'foo.flac')
    operation_id = mover.move(src, dst)
    self.assertTrue(self._wait_for_status(mover, operation_id, bf_file_mover_status.done))
    self.assertEqual(b'test content', open(dst, 'rb').read())
    mover.stop_worker()

  def test_move_same_device_status_done(self):
    mover = self._make_mover()
    mover.start_worker()
    src = self._make_source_file()
    dst_dir = self.make_temp_dir()
    dst = path.join(dst_dir, 'foo.flac')
    operation_id = mover.move(src, dst)
    self._wait_for_status(mover, operation_id, bf_file_mover_status.done)
    self.assertEqual(bf_file_mover_status.done, mover.status(operation_id))
    mover.stop_worker()

  def test_move_same_device_uuid_dir_removed(self):
    mover = self._make_mover()
    mover.start_worker()
    src = self._make_source_file()
    dst_dir = self.make_temp_dir()
    dst = path.join(dst_dir, 'foo.flac')
    operation_id = mover.move(src, dst)
    operation = mover.operation(operation_id)
    staging_uuid_dir = path.dirname(operation.staging_path)
    self._wait_for_status(mover, operation_id, bf_file_mover_status.done)
    self.assertFalse(path.exists(staging_uuid_dir))
    mover.stop_worker()

  def test_move_to_existing_deep_destination(self):
    mover = self._make_mover()
    mover.start_worker()
    src = self._make_source_file()
    dst_base = self.make_temp_dir()
    os.makedirs(path.join(dst_base, 'deep', 'nested', 'dir'))
    dst = path.join(dst_base, 'deep', 'nested', 'dir', 'foo.flac')
    operation_id = mover.move(src, dst)
    self.assertTrue(self._wait_for_status(mover, operation_id, bf_file_mover_status.done))
    self.assertTrue(path.exists(dst))
    mover.stop_worker()

  # cross-device copy (forced via mock)

  def test_move_cross_device_completes(self):
    mover = self._make_mover()
    mover.start_worker()
    src = self._make_source_file(content='cross device data')
    dst_dir = self.make_temp_dir()
    dst = path.join(dst_dir, 'foo.flac')
    with mock.patch.object(mover._worker, '_same_device', return_value=False):
      operation_id = mover.move(src, dst)
      self.assertTrue(self._wait_for_status(mover, operation_id, bf_file_mover_status.done))
    self.assertEqual(b'cross device data', open(dst, 'rb').read())
    mover.stop_worker()

  def test_move_cross_device_staging_file_removed(self):
    mover = self._make_mover()
    mover.start_worker()
    src = self._make_source_file()
    dst_dir = self.make_temp_dir()
    dst = path.join(dst_dir, 'foo.flac')
    with mock.patch.object(mover._worker, '_same_device', return_value=False):
      operation_id = mover.move(src, dst)
      operation = mover.operation(operation_id)
      staging_path = operation.staging_path
      self._wait_for_status(mover, operation_id, bf_file_mover_status.done)
    self.assertFalse(path.exists(staging_path))
    mover.stop_worker()

  def test_move_cross_device_uuid_dir_removed(self):
    mover = self._make_mover()
    mover.start_worker()
    src = self._make_source_file()
    dst_dir = self.make_temp_dir()
    dst = path.join(dst_dir, 'foo.flac')
    with mock.patch.object(mover._worker, '_same_device', return_value=False):
      operation_id = mover.move(src, dst)
      operation = mover.operation(operation_id)
      staging_uuid_dir = path.dirname(operation.staging_path)
      self._wait_for_status(mover, operation_id, bf_file_mover_status.done)
    self.assertFalse(path.exists(staging_uuid_dir))
    mover.stop_worker()

  def test_move_cross_device_status_transitions(self):
    statuses = []
    def on_complete(operation_id):
      statuses.append('complete')

    options = bf_file_mover_options(on_complete=on_complete)
    mover = self._make_mover(options=options)
    mover.start_worker()
    src = self._make_source_file()
    dst = path.join(self.make_temp_dir(), 'foo.flac')
    with mock.patch.object(mover._worker, '_same_device', return_value=False):
      operation_id = mover.move(src, dst)
      self._wait_for_status(mover, operation_id, bf_file_mover_status.done)
    self.assertEqual(['complete'], statuses)
    mover.stop_worker()

  # checksum verification

  def test_checksum_verification_passes(self):
    options = bf_file_mover_options(verify_checksum_after_copy=True)
    mover = self._make_mover(options=options)
    mover.start_worker()
    src = self._make_source_file(content='checksum content')
    dst = path.join(self.make_temp_dir(), 'foo.flac')
    with mock.patch.object(mover._worker, '_same_device', return_value=False):
      operation_id = mover.move(src, dst)
      self.assertTrue(self._wait_for_status(mover, operation_id, bf_file_mover_status.done))
    mover.stop_worker()

  # callbacks

  def test_on_complete_fires(self):
    completed = []
    options = bf_file_mover_options(on_complete=lambda op_id: completed.append(op_id))
    mover = self._make_mover(options=options)
    mover.start_worker()
    src = self._make_source_file()
    dst = path.join(self.make_temp_dir(), 'foo.flac')
    operation_id = mover.move(src, dst)
    self._wait_for_status(mover, operation_id, bf_file_mover_status.done)
    self.assertEqual([operation_id], completed)
    mover.stop_worker()

  def test_on_progress_fires(self):
    progress_calls = []
    def on_progress(op_id, bytes_copied, total_bytes):
      progress_calls.append((bytes_copied, total_bytes))

    options = bf_file_mover_options(on_progress=on_progress)
    mover = self._make_mover(options=options)
    mover.start_worker()
    src = self._make_source_file(content='a' * 1024)
    dst = path.join(self.make_temp_dir(), 'foo.flac')
    with mock.patch.object(mover._worker, '_same_device', return_value=False):
      operation_id = mover.move(src, dst)
      self._wait_for_status(mover, operation_id, bf_file_mover_status.done)
    self.assertGreater(len(progress_calls), 0)
    mover.stop_worker()

  def test_on_progress_total_bytes_correct(self):
    total_bytes_seen = []
    content = 'x' * 2048
    def on_progress(op_id, bytes_copied, total_bytes):
      total_bytes_seen.append(total_bytes)

    options = bf_file_mover_options(on_progress=on_progress)
    mover = self._make_mover(options=options)
    mover.start_worker()
    src = self._make_source_file(content=content)
    dst = path.join(self.make_temp_dir(), 'foo.flac')
    with mock.patch.object(mover._worker, '_same_device', return_value=False):
      operation_id = mover.move(src, dst)
      self._wait_for_status(mover, operation_id, bf_file_mover_status.done)
    self.assertTrue(all(t == len(content) for t in total_bytes_seen))
    mover.stop_worker()

  def test_on_pause_fires(self):
    paused = []
    options = bf_file_mover_options(on_pause=lambda op_id: paused.append(op_id))
    mover = self._make_mover(options=options)
    mover.start_worker()
    src = self._make_source_file()
    nonexistent_dst = path.join(self.make_temp_dir(), 'absent_dir', 'foo.flac')
    operation_id = mover.move(src, nonexistent_dst)
    self._wait_for_status(mover, operation_id, bf_file_mover_status.paused)
    self.assertEqual([operation_id], paused)
    mover.stop_worker()

  # paused — destination unavailable

  def test_pauses_when_destination_dir_missing(self):
    mover = self._make_mover()
    mover.start_worker()
    src = self._make_source_file()
    dst = path.join(self.make_temp_dir(), 'missing', 'foo.flac')
    operation_id = mover.move(src, dst)
    self.assertTrue(self._wait_for_status(mover, operation_id, bf_file_mover_status.paused))
    mover.stop_worker()

  def test_staging_file_preserved_when_paused(self):
    mover = self._make_mover()
    mover.start_worker()
    src = self._make_source_file()
    dst = path.join(self.make_temp_dir(), 'missing', 'foo.flac')
    operation_id = mover.move(src, dst)
    self._wait_for_status(mover, operation_id, bf_file_mover_status.paused)
    operation = mover.operation(operation_id)
    self.assertTrue(path.exists(operation.staging_path))
    mover.stop_worker()

  def test_destination_device_id_recorded_when_dir_exists(self):
    mover = self._make_mover()
    mover.start_worker()
    src = self._make_source_file()
    dst_dir = self.make_temp_dir()
    dst = path.join(dst_dir, 'foo.flac')
    operation_id = mover.move(src, dst)
    operation = mover.operation(operation_id)
    self.assertIsNotNone(operation.destination_device_id)
    mover.stop_worker()

  def test_destination_device_id_null_when_dir_missing(self):
    mover = self._make_mover()
    mover.start_worker()
    src = self._make_source_file()
    dst = path.join(self.make_temp_dir(), 'missing_dir', 'foo.flac')
    operation_id = mover.move(src, dst)
    operation = mover.operation(operation_id)
    self.assertIsNone(operation.destination_device_id)
    mover.stop_worker()

  def test_resume_paused_requeues_when_destination_available(self):
    mover = self._make_mover()
    mover.start_worker()
    src = self._make_source_file()
    dst_base = self.make_temp_dir()
    dst_dir = path.join(dst_base, 'soon')
    dst = path.join(dst_dir, 'foo.flac')
    operation_id = mover.move(src, dst)
    self._wait_for_status(mover, operation_id, bf_file_mover_status.paused)
    os.makedirs(dst_dir)
    mover.resume_paused()
    self.assertTrue(self._wait_for_status(mover, operation_id, bf_file_mover_status.done))
    mover.stop_worker()

  def test_resume_paused_leaves_paused_when_still_missing(self):
    mover = self._make_mover()
    mover.start_worker()
    src = self._make_source_file()
    dst = path.join(self.make_temp_dir(), 'never_exists', 'foo.flac')
    operation_id = mover.move(src, dst)
    self._wait_for_status(mover, operation_id, bf_file_mover_status.paused)
    mover.resume_paused()
    time.sleep(0.2)
    self.assertEqual(bf_file_mover_status.paused, mover.status(operation_id))
    mover.stop_worker()

  def test_resume_paused_raises_if_worker_not_running(self):
    mover = self._make_mover()
    with self.assertRaises(RuntimeError):
      mover.resume_paused()

  # recovery scan at startup

  def test_recovery_resumes_interrupted_copy(self):
    database_path = path.join(self.make_temp_dir(), 'move.sqlite')
    src = self._make_source_file(content='recovery content')
    dst_dir = self.make_temp_dir()
    dst = path.join(dst_dir, 'foo.flac')

    db = bf_file_mover_database(database_path)
    now = int(time.time())
    staging_dir = self.make_temp_dir()
    staging_uuid_dir = path.join(staging_dir, 'test-uuid-001')
    os.makedirs(staging_uuid_dir)
    staging_path = path.join(staging_uuid_dir, 'foo.flac')
    os.rename(src, staging_path)

    op = bf_file_mover_operation(
      operation_id='test-uuid-001',
      source_path=src,
      staging_path=staging_path,
      destination_path=dst,
      destination_device_id=None,
      status=bf_file_mover_status.copying,
      submitted_at=now,
      staged_at=now,
      copy_started_at=now,
    )
    db.insert_operation(op)

    mover = bf_file_mover(database_path)
    mover.start_worker()
    self.assertTrue(self._wait_for_status(mover, 'test-uuid-001', bf_file_mover_status.done))
    self.assertTrue(path.exists(dst))
    mover.stop_worker()

  def test_recovery_fails_interrupted_copy_missing_staging(self):
    database_path = path.join(self.make_temp_dir(), 'move.sqlite')
    db = bf_file_mover_database(database_path)
    now = int(time.time())
    op = bf_file_mover_operation(
      operation_id='missing-staging-op',
      source_path='/src/foo.flac',
      staging_path='/nonexistent/staging/uuid/foo.flac',
      destination_path='/dst/foo.flac',
      destination_device_id=None,
      status=bf_file_mover_status.copying,
      submitted_at=now,
      staged_at=now,
    )
    db.insert_operation(op)

    mover = bf_file_mover(database_path)
    mover.start_worker()
    time.sleep(0.2)
    self.assertEqual(bf_file_mover_status.failed, mover.status('missing-staging-op'))
    mover.stop_worker()

  def test_start_worker_resumes_paused_on_startup(self):
    database_path = path.join(self.make_temp_dir(), 'move.sqlite')
    dst_dir = self.make_temp_dir()
    dst = path.join(dst_dir, 'foo.flac')
    src = self._make_source_file(content='paused recovery')

    db = bf_file_mover_database(database_path)
    now = int(time.time())
    staging_dir = self.make_temp_dir()
    staging_uuid_dir = path.join(staging_dir, 'paused-uuid-001')
    os.makedirs(staging_uuid_dir)
    staging_path = path.join(staging_uuid_dir, 'foo.flac')
    os.rename(src, staging_path)

    op = bf_file_mover_operation(
      operation_id='paused-uuid-001',
      source_path=src,
      staging_path=staging_path,
      destination_path=dst,
      destination_device_id=None,
      status=bf_file_mover_status.paused,
      submitted_at=now,
      staged_at=now,
      paused_at=now,
    )
    db.insert_operation(op)

    mover = bf_file_mover(database_path)
    mover.start_worker()
    self.assertTrue(self._wait_for_status(mover, 'paused-uuid-001', bf_file_mover_status.done))
    self.assertTrue(path.exists(dst))
    mover.stop_worker()

  # orphans

  def test_list_orphans_finds_untracked_file(self):
    mover = self._make_mover()
    mover.start_worker()
    src = self._make_source_file()
    dst = path.join(self.make_temp_dir(), 'foo.flac')
    operation_id = mover.move(src, dst)
    operation = mover.operation(operation_id)

    staging_root = path.dirname(path.dirname(operation.staging_path))
    orphan_uuid_dir = path.join(staging_root, 'orphan-uuid-xyz')
    os.makedirs(orphan_uuid_dir)
    orphan_file = path.join(orphan_uuid_dir, 'orphan.flac')
    with open(orphan_file, 'wb') as f:
      f.write(b'orphan data')

    orphans = mover.list_orphans()
    self.assertIn(orphan_file, orphans)
    mover.stop_worker()

  def test_list_orphans_empty_when_all_tracked(self):
    mover = self._make_mover()
    mover.start_worker()
    src = self._make_source_file()
    dst = path.join(self.make_temp_dir(), 'missing_dir', 'foo.flac')
    mover.move(src, dst)
    time.sleep(0.2)
    orphans = mover.list_orphans()
    self.assertEqual([], orphans)
    mover.stop_worker()

  def test_orphan_not_deleted_automatically(self):
    mover = self._make_mover()
    mover.start_worker()
    src_for_known = self._make_source_file(filename='known.flac')
    dst_for_known = path.join(self.make_temp_dir(), 'missing', 'known.flac')
    operation_id = mover.move(src_for_known, dst_for_known)
    operation = mover.operation(operation_id)

    staging_root = path.dirname(path.dirname(operation.staging_path))
    orphan_uuid_dir = path.join(staging_root, 'orphan-no-delete')
    os.makedirs(orphan_uuid_dir)
    orphan_file = path.join(orphan_uuid_dir, 'data.flac')
    with open(orphan_file, 'wb') as f:
      f.write(b'keep me')

    mover.stop_worker()
    mover2 = bf_file_mover(mover._database_path)
    mover2.start_worker()
    time.sleep(0.3)
    self.assertTrue(path.exists(orphan_file))
    mover2.stop_worker()

  # error handling

  def test_staging_rename_fails_source_untouched(self):
    mover = self._make_mover()
    mover.start_worker()
    src = self._make_source_file()
    dst = path.join(self.make_temp_dir(), 'foo.flac')

    with mock.patch('os.rename', side_effect=OSError('simulated rename failure')):
      with self.assertRaises(OSError):
        mover.move(src, dst)

    self.assertTrue(path.exists(src))
    mover.stop_worker()

  def test_mid_copy_failure_preserves_staging_file(self):
    mover = self._make_mover()
    mover.start_worker()
    src = self._make_source_file(content='content')
    dst = path.join(self.make_temp_dir(), 'foo.flac')

    call_count = [0]
    original_open = open
    def failing_open(filepath, mode='r', **kwargs):
      if 'w' in mode and filepath == dst:
        call_count[0] += 1
        raise OSError('simulated write failure')
      return original_open(filepath, mode, **kwargs)

    with mock.patch('builtins.open', side_effect=failing_open):
      with mock.patch.object(mover._worker, '_same_device', return_value=False):
        operation_id = mover.move(src, dst)
        self._wait_for_status(mover, operation_id, bf_file_mover_status.failed)

    operation = mover.operation(operation_id)
    self.assertTrue(path.exists(operation.staging_path))
    mover.stop_worker()

  def test_mid_copy_failure_deletes_partial_destination(self):
    mover = self._make_mover()
    mover.start_worker()
    src = self._make_source_file(content='content')
    dst_dir = self.make_temp_dir()
    dst = path.join(dst_dir, 'foo.flac')

    written = [False]
    original_open = open

    def partially_writing_open(filepath, mode='r', **kwargs):
      if 'w' in mode and filepath == dst:
        class PartialWriter:
          def __init__(self):
            self._f = original_open(filepath, mode, **kwargs)
          def write(self, data):
            written[0] = True
            raise OSError('disk full')
          def __enter__(self): return self
          def __exit__(self, *args):
            self._f.close()
            return False
          def flush(self): pass
          def fileno(self): return self._f.fileno()
        return PartialWriter()
      return original_open(filepath, mode, **kwargs)

    with mock.patch('builtins.open', side_effect=partially_writing_open):
      with mock.patch.object(mover._worker, '_same_device', return_value=False):
        operation_id = mover.move(src, dst)
        self._wait_for_status(mover, operation_id, bf_file_mover_status.failed)

    self.assertFalse(path.exists(dst))
    mover.stop_worker()

  def test_retry_requeues_with_staging_file(self):
    mover = self._make_mover()
    mover.start_worker()
    src = self._make_source_file(content='retry me')
    dst = path.join(self.make_temp_dir(), 'missing_dir', 'foo.flac')
    operation_id = mover.move(src, dst)
    self._wait_for_status(mover, operation_id, bf_file_mover_status.paused)

    mover._database.update_status(operation_id, bf_file_mover_status.failed)

    dst_dir = path.dirname(dst)
    os.makedirs(dst_dir)
    mover.retry(operation_id)
    self.assertTrue(self._wait_for_status(mover, operation_id, bf_file_mover_status.done))
    mover.stop_worker()

  def test_retry_raises_without_staging_file(self):
    mover = self._make_mover()
    mover.start_worker()
    database_path = mover._database_path
    now = int(time.time())
    op = bf_file_mover_operation(
      operation_id='no-staging',
      source_path='/src/foo.flac',
      staging_path='/nonexistent/staging/no-staging/foo.flac',
      destination_path=path.join(self.make_temp_dir(), 'foo.flac'),
      destination_device_id=None,
      status=bf_file_mover_status.failed,
      submitted_at=now,
      staged_at=now,
    )
    mover._database.insert_operation(op)
    with self.assertRaises(RuntimeError):
      mover.retry('no-staging')
    mover.stop_worker()

  def test_retry_raises_on_expired_operation(self):
    mover = self._make_mover()
    mover.start_worker()
    now = int(time.time())
    op = bf_file_mover_operation(
      operation_id='expired-op',
      source_path='/src/foo.flac',
      staging_path='/staging/expired-op/foo.flac',
      destination_path='/dst/foo.flac',
      destination_device_id=None,
      status=bf_file_mover_status.expired,
      submitted_at=now,
      staged_at=now,
    )
    mover._database.insert_operation(op)
    with self.assertRaises(RuntimeError):
      mover.retry('expired-op')
    mover.stop_worker()

  # vacuum_staging

  def test_vacuum_removes_old_failed_staging_file(self):
    mover = self._make_mover()
    mover.start_worker()
    src = self._make_source_file()
    dst = path.join(self.make_temp_dir(), 'missing_dir', 'foo.flac')
    operation_id = mover.move(src, dst)
    self._wait_for_status(mover, operation_id, bf_file_mover_status.paused)

    mover._database.update_status(
      operation_id,
      bf_file_mover_status.failed,
      completed_at=int(time.time()) - 100
    )

    operation = mover.operation(operation_id)
    staging_path = operation.staging_path
    staging_uuid_dir = path.dirname(staging_path)

    mover.vacuum_staging(minimum_age_days=0)

    self.assertFalse(path.exists(staging_path))
    self.assertFalse(path.exists(staging_uuid_dir))
    self.assertEqual(bf_file_mover_status.expired, mover.status(operation_id))
    mover.stop_worker()

  def test_vacuum_preserves_recent_failed(self):
    mover = self._make_mover()
    mover.start_worker()
    src = self._make_source_file()
    dst = path.join(self.make_temp_dir(), 'missing_dir', 'foo.flac')
    operation_id = mover.move(src, dst)
    self._wait_for_status(mover, operation_id, bf_file_mover_status.paused)
    mover._database.update_status(operation_id, bf_file_mover_status.failed, completed_at=int(time.time()))

    mover.vacuum_staging(minimum_age_days=30)

    operation = mover.operation(operation_id)
    self.assertTrue(path.exists(operation.staging_path))
    self.assertEqual(bf_file_mover_status.failed, mover.status(operation_id))
    mover.stop_worker()

  def test_vacuum_preserves_paused_with_intact_staging(self):
    mover = self._make_mover()
    mover.start_worker()
    src = self._make_source_file()
    dst = path.join(self.make_temp_dir(), 'missing_dir', 'foo.flac')
    operation_id = mover.move(src, dst)
    self._wait_for_status(mover, operation_id, bf_file_mover_status.paused)

    mover.vacuum_staging(minimum_age_days=0)

    operation = mover.operation(operation_id)
    self.assertTrue(path.exists(operation.staging_path))
    self.assertEqual(bf_file_mover_status.paused, mover.status(operation_id))
    mover.stop_worker()

  def test_vacuum_removes_paused_with_missing_staging(self):
    mover = self._make_mover()
    mover.start_worker()
    now = int(time.time())
    staging_uuid_dir = path.join(self.make_temp_dir(), 'ghost-uuid')
    op = bf_file_mover_operation(
      operation_id='ghost-uuid',
      source_path='/src/foo.flac',
      staging_path=path.join(staging_uuid_dir, 'foo.flac'),
      destination_path='/dst/foo.flac',
      destination_device_id=None,
      status=bf_file_mover_status.paused,
      submitted_at=now,
      staged_at=now,
      paused_at=now,
    )
    mover._database.insert_operation(op)

    mover.vacuum_staging(minimum_age_days=0)

    self.assertEqual(bf_file_mover_status.expired, mover.status('ghost-uuid'))
    mover.stop_worker()

  def test_vacuum_expired_records_remain_in_database(self):
    mover = self._make_mover()
    mover.start_worker()
    src = self._make_source_file()
    dst = path.join(self.make_temp_dir(), 'missing_dir', 'foo.flac')
    operation_id = mover.move(src, dst)
    self._wait_for_status(mover, operation_id, bf_file_mover_status.paused)
    mover._database.update_status(
      operation_id,
      bf_file_mover_status.failed,
      completed_at=int(time.time()) - 100
    )

    mover.vacuum_staging(minimum_age_days=0)

    operation = mover.operation(operation_id)
    self.assertIsNotNone(operation)
    self.assertEqual(bf_file_mover_status.expired, operation.status)
    mover.stop_worker()

  def test_vacuum_expired_not_retriable(self):
    mover = self._make_mover()
    mover.start_worker()
    now = int(time.time())
    op = bf_file_mover_operation(
      operation_id='already-expired',
      source_path='/src/foo.flac',
      staging_path='/staging/already-expired/foo.flac',
      destination_path='/dst/foo.flac',
      destination_device_id=None,
      status=bf_file_mover_status.expired,
      submitted_at=now,
      staged_at=now,
    )
    mover._database.insert_operation(op)
    with self.assertRaises(RuntimeError):
      mover.retry('already-expired')
    mover.stop_worker()

  # concurrency

  def test_multiple_files_queued_all_complete(self):
    mover = self._make_mover()
    mover.start_worker()
    dst_dir = self.make_temp_dir()
    operation_ids = []
    for i in range(5):
      src = self._make_source_file(content=f'file{i}', filename=f'track{i}.flac')
      os.makedirs(path.join(dst_dir, f'sub{i}'))
      dst = path.join(dst_dir, f'sub{i}', f'track{i}.flac')
      operation_ids.append(mover.move(src, dst))

    for operation_id in operation_ids:
      self.assertTrue(self._wait_for_status(mover, operation_id, bf_file_mover_status.done))

    for i in range(5):
      self.assertEqual(f'file{i}'.encode(), open(path.join(dst_dir, f'sub{i}', f'track{i}.flac'), 'rb').read())
    mover.stop_worker()

if __name__ == '__main__':
  unit_test.main()

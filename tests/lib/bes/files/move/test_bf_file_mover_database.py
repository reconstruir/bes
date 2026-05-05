#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import time
import unittest
from os import path

from bes.testing.unit_test import unit_test
from bes.files.move.bf_file_mover_database import bf_file_mover_database
from bes.files.move.bf_file_mover_operation import bf_file_mover_operation
from bes.files.move.bf_file_mover_status import bf_file_mover_status

class test_bf_file_mover_database(unit_test):

  def _make_database(self):
    database_path = path.join(self.make_temp_dir(), 'test_move.sqlite')
    return bf_file_mover_database(database_path)

  def _make_operation(self, operation_id='op-001', status=bf_file_mover_status.staging_done):
    now = int(time.time())
    return bf_file_mover_operation(
      operation_id=operation_id,
      source_path='/src/foo.flac',
      staging_path='/staging/op-001/foo.flac',
      destination_path='/dst/foo.flac',
      destination_device_id='42',
      status=status,
      submitted_at=now,
      staged_at=now,
    )

  # schema

  def test_create_and_schema_version(self):
    db = self._make_database()
    self.assertEqual(1, db.schema_version())

  def test_database_file_created(self):
    database_path = path.join(self.make_temp_dir(), 'sub', 'test.sqlite')
    bf_file_mover_database(database_path)
    self.assertTrue(path.exists(database_path))

  # insert and retrieve

  def test_insert_and_retrieve(self):
    db = self._make_database()
    op = self._make_operation()
    db.insert_operation(op)
    retrieved = db.get_operation('op-001')
    self.assertIsNotNone(retrieved)
    self.assertEqual('op-001', retrieved.operation_id)
    self.assertEqual('/src/foo.flac', retrieved.source_path)
    self.assertEqual('/staging/op-001/foo.flac', retrieved.staging_path)
    self.assertEqual('/dst/foo.flac', retrieved.destination_path)
    self.assertEqual('42', retrieved.destination_device_id)
    self.assertEqual(bf_file_mover_status.staging_done, retrieved.status)

  def test_get_nonexistent_operation_returns_none(self):
    db = self._make_database()
    self.assertIsNone(db.get_operation('no-such-id'))

  def test_destination_device_id_can_be_none(self):
    db = self._make_database()
    now = int(time.time())
    op = bf_file_mover_operation(
      operation_id='op-none',
      source_path='/src/foo.flac',
      staging_path='/staging/op-none/foo.flac',
      destination_path='/dst/foo.flac',
      destination_device_id=None,
      status=bf_file_mover_status.staging_done,
      submitted_at=now,
    )
    db.insert_operation(op)
    retrieved = db.get_operation('op-none')
    self.assertIsNone(retrieved.destination_device_id)

  # update_status

  def test_update_status(self):
    db = self._make_database()
    op = self._make_operation()
    db.insert_operation(op)
    db.update_status('op-001', bf_file_mover_status.copying, copy_started_at=12345)
    retrieved = db.get_operation('op-001')
    self.assertEqual(bf_file_mover_status.copying, retrieved.status)
    self.assertEqual(12345, retrieved.copy_started_at)

  def test_update_status_to_done(self):
    db = self._make_database()
    op = self._make_operation()
    db.insert_operation(op)
    db.update_status('op-001', bf_file_mover_status.done, completed_at=99999)
    retrieved = db.get_operation('op-001')
    self.assertEqual(bf_file_mover_status.done, retrieved.status)
    self.assertEqual(99999, retrieved.completed_at)

  def test_update_status_to_failed_with_message(self):
    db = self._make_database()
    op = self._make_operation()
    db.insert_operation(op)
    db.update_status('op-001', bf_file_mover_status.failed, error_message='disk full')
    retrieved = db.get_operation('op-001')
    self.assertEqual(bf_file_mover_status.failed, retrieved.status)
    self.assertEqual('disk full', retrieved.error_message)

  def test_update_status_unknown_field_raises(self):
    db = self._make_database()
    op = self._make_operation()
    db.insert_operation(op)
    with self.assertRaises(ValueError):
      db.update_status('op-001', bf_file_mover_status.failed, bogus_field='oops')

  # list_operations

  def test_list_operations_all(self):
    db = self._make_database()
    db.insert_operation(self._make_operation('op-1', bf_file_mover_status.staging_done))
    db.insert_operation(self._make_operation('op-2', bf_file_mover_status.done))
    db.insert_operation(self._make_operation('op-3', bf_file_mover_status.failed))
    all_ops = db.list_operations()
    self.assertEqual(3, len(all_ops))

  def test_list_operations_by_status(self):
    db = self._make_database()
    db.insert_operation(self._make_operation('op-1', bf_file_mover_status.staging_done))
    db.insert_operation(self._make_operation('op-2', bf_file_mover_status.done))
    db.insert_operation(self._make_operation('op-3', bf_file_mover_status.staging_done))
    staging_done = db.list_operations(status=bf_file_mover_status.staging_done)
    self.assertEqual(2, len(staging_done))
    self.assertEqual({'op-1', 'op-3'}, {op.operation_id for op in staging_done})

  def test_list_operations_by_status_empty(self):
    db = self._make_database()
    result = db.list_operations(status=bf_file_mover_status.paused)
    self.assertEqual([], result)

  def test_list_operations_since(self):
    db = self._make_database()
    now = int(time.time())
    op_old = bf_file_mover_operation(
      operation_id='old', source_path='/s/f', staging_path='/t/old/f',
      destination_path='/d/f', destination_device_id=None,
      status=bf_file_mover_status.done, submitted_at=now - 1000, staged_at=now - 1000,
    )
    op_new = bf_file_mover_operation(
      operation_id='new', source_path='/s/f', staging_path='/t/new/f',
      destination_path='/d/f', destination_device_id=None,
      status=bf_file_mover_status.done, submitted_at=now, staged_at=now,
    )
    db.insert_operation(op_old)
    db.insert_operation(op_new)
    result = db.list_operations(since=now - 500)
    self.assertEqual(1, len(result))
    self.assertEqual('new', result[0].operation_id)

  def test_list_operations_ordered_by_submitted_at(self):
    db = self._make_database()
    now = int(time.time())
    for i in range(3):
      op = bf_file_mover_operation(
        operation_id=f'op-{i}', source_path='/s/f', staging_path=f'/t/op-{i}/f',
        destination_path='/d/f', destination_device_id=None,
        status=bf_file_mover_status.done, submitted_at=now + i,
      )
      db.insert_operation(op)
    result = db.list_operations()
    ids = [op.operation_id for op in result]
    self.assertEqual(['op-0', 'op-1', 'op-2'], ids)

if __name__ == '__main__':
  unit_test.main()

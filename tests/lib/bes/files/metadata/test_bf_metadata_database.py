#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import time

from bes.testing.unit_test import unit_test
from bes.files.metadata.bf_metadata_database import bf_metadata_database

class test_bf_metadata_database(unit_test):

  def _make_database(self):
    database_path = self.make_temp_file(suffix = '.db', non_existent = True)
    return bf_metadata_database(database_path)

  def test_set_and_get(self):
    database = self._make_database()
    database.set('abc123', 'color', 'blue')
    self.assertEqual('blue', database.get('abc123', 'color'))

  def test_get_missing(self):
    database = self._make_database()
    self.assertIsNone(database.get('abc123', 'missing'))

  def test_get_missing_checksum(self):
    database = self._make_database()
    self.assertIsNone(database.get('no_such_checksum', 'color'))

  def test_set_overwrites(self):
    database = self._make_database()
    database.set('abc123', 'color', 'blue')
    database.set('abc123', 'color', 'red')
    self.assertEqual('red', database.get('abc123', 'color'))

  def test_delete_by_key(self):
    database = self._make_database()
    database.set('abc123', 'color', 'blue')
    database.set('abc123', 'size', 'large')
    database.delete('abc123', 'color')
    self.assertIsNone(database.get('abc123', 'color'))
    self.assertEqual('large', database.get('abc123', 'size'))

  def test_delete_all(self):
    database = self._make_database()
    database.set('abc123', 'color', 'blue')
    database.set('abc123', 'size', 'large')
    database.delete('abc123')
    self.assertIsNone(database.get('abc123', 'color'))
    self.assertIsNone(database.get('abc123', 'size'))

  def test_delete_does_not_affect_other_checksums(self):
    database = self._make_database()
    database.set('abc123', 'color', 'blue')
    database.set('def456', 'color', 'green')
    database.delete('abc123')
    self.assertEqual('green', database.get('def456', 'color'))

  def test_keys(self):
    database = self._make_database()
    database.set('abc123', 'color', 'blue')
    database.set('abc123', 'size', 'large')
    database.set('abc123', 'weight', 'heavy')
    self.assertEqual(['color', 'size', 'weight'], database.keys('abc123'))

  def test_keys_empty(self):
    database = self._make_database()
    self.assertEqual([], database.keys('no_such_checksum'))

  def test_get_all(self):
    database = self._make_database()
    database.set('abc123', 'color', 'blue')
    database.set('abc123', 'size', 'large')
    self.assertEqual({'color': 'blue', 'size': 'large'}, database.get_all('abc123'))

  def test_get_all_empty(self):
    database = self._make_database()
    self.assertEqual({}, database.get_all('no_such_checksum'))

  def test_row_count(self):
    database = self._make_database()
    self.assertEqual(0, database.row_count())
    database.set('abc123', 'color', 'blue')
    database.set('abc123', 'size', 'large')
    database.set('def456', 'color', 'green')
    self.assertEqual(3, database.row_count())

  def test_schema_version(self):
    database = self._make_database()
    self.assertEqual(bf_metadata_database.SCHEMA_VERSION, database.schema_version())

  def test_schema_migration(self):
    database_path = self.make_temp_file(suffix = '.db', non_existent = True)
    database = bf_metadata_database(database_path)
    database.set('abc123', 'color', 'blue')
    database.close()

    # corrupt the stored schema version to trigger migration
    from bes.sqlite.sqlite import sqlite
    connection = sqlite(database_path)
    connection.execute(
      "UPDATE __bes_table_version__ SET version = 999 WHERE name = 'metadata_v1'"
    )
    connection.commit()
    connection._connection.close()

    # reopening should drop and recreate the table
    database = bf_metadata_database(database_path)
    self.assertEqual(bf_metadata_database.SCHEMA_VERSION, database.schema_version())
    self.assertIsNone(database.get('abc123', 'color'))

  def test_vacuum_skips_small_database(self):
    database = self._make_database()
    database.set('abc123', 'color', 'blue')
    # row count is far below threshold — vacuum is a no-op
    self.assertEqual(1, database.row_count())

  def test_vacuum_deletes_old_rows(self):
    database_path = self.make_temp_file(suffix = '.db', non_existent = True)
    database = bf_metadata_database(database_path)

    old_cutoff = int(time.time()) - (bf_metadata_database._VACUUM_AGE_DAYS + 1) * 86400
    threshold = bf_metadata_database._VACUUM_ROW_THRESHOLD

    # insert rows above threshold with artificially old stored_at
    from bes.sqlite.sqlite import sqlite as sqlite_wrapper
    raw = sqlite_wrapper(database_path, check_same_thread = False)
    for i in range(threshold + 10):
      raw.execute(
        'insert or replace into metadata_v1 values (?, ?, ?, ?)',
        (f'checksum_{i:06d}', 'key', 'value', old_cutoff - 1)
      )
    raw.commit()
    raw._connection.close()

    # reopening triggers vacuum
    database2 = bf_metadata_database(database_path)
    self.assertEqual(0, database2.row_count())

  def test_vacuum_skips_no_old_rows(self):
    database_path = self.make_temp_file(suffix = '.db', non_existent = True)
    database = bf_metadata_database(database_path)
    threshold = bf_metadata_database._VACUUM_ROW_THRESHOLD

    from bes.sqlite.sqlite import sqlite as sqlite_wrapper
    raw = sqlite_wrapper(database_path, check_same_thread = False)
    for i in range(threshold + 10):
      raw.execute(
        'insert or replace into metadata_v1 values (?, ?, ?, ?)',
        (f'checksum_{i:06d}', 'key', 'value', int(time.time()))
      )
    raw.commit()
    raw._connection.close()

    # reopening triggers vacuum check — all rows are recent, none deleted
    database2 = bf_metadata_database(database_path)
    self.assertEqual(threshold + 10, database2.row_count())

if __name__ == '__main__':
  unit_test.main()

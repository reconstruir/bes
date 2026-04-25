#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
import time

from bes.files.metadata.bf_metadata import bf_metadata
from bes.files.metadata.bf_metadata_file import bf_metadata_file
from bes.files.metadata.bf_metadata_file_store import bf_metadata_file_store
from bes.testing.unit_test import unit_test

from _bes_unit_test_common.files.metadata.example_metadata_fruits_factory import example_metadata_fruits_factory

class test_bf_metadata_file(unit_test):

  def setUp(self):
    db_path = self.make_temp_file(suffix = '.db', non_existent = True)
    bf_metadata._set_file_store(bf_metadata_file_store(database_path = db_path))
    bf_metadata._items.clear()

  def tearDown(self):
    bf_metadata._set_file_store(None)
    bf_metadata._items.clear()

  def test_get_metadata(self):
    tmp = bf_metadata_file(self.make_temp_file(dir = __file__, non_existent = True, suffix = '.data'))

    with open(tmp.filename, 'wb') as fout:
      fout.write(b'12345')
      fout.flush()
      os.fsync(fout.fileno())

      self.assertEqual( 0, tmp.get_metadata_getter_count('acme__fruit__kiwi__1.0') )
      self.assertEqual( 0, tmp.get_metadata_getter_count('acme__fruit__kiwi__1.0') )
      self.assertEqual( 5, tmp.get_metadata('acme__fruit__kiwi__1.0') )
      self.assertEqual( 1, tmp.get_metadata_getter_count('acme__fruit__kiwi__1.0') )
      self.assertEqual( 5, tmp.get_metadata('acme__fruit__kiwi__1.0') )
      self.assertEqual( 1, tmp.get_metadata_getter_count('acme__fruit__kiwi__1.0') )
      self.assertEqual( ['acme__fruit__kiwi__1.0'], tmp.keys() )

      self.assertEqual( 0, tmp.get_metadata_getter_count('acme__fruit__cherry__2.0') )
      self.assertEqual( 2.5, tmp.get_metadata('acme__fruit__cherry__2.0') )
      self.assertEqual( 1, tmp.get_metadata_getter_count('acme__fruit__cherry__2.0') )
      self.assertEqual( 2.5, tmp.get_metadata('acme__fruit__cherry__2.0') )
      self.assertEqual( 1, tmp.get_metadata_getter_count('acme__fruit__cherry__2.0') )

      self.assertEqual( [
        'acme__fruit__cherry__2.0',
        'acme__fruit__kiwi__1.0',
      ], tmp.keys() )

      time.sleep(.01)
      fout.seek(0)
      fout.truncate(0)
      fout.write(b'1234567890')
      time.sleep(10.0)
      fout.flush()
      os.fsync(fout.fileno())

      self.assertEqual( 1, tmp.get_metadata_getter_count('acme__fruit__kiwi__1.0') )
      self.assertEqual( 10, tmp.get_metadata('acme__fruit__kiwi__1.0') )
      self.assertEqual( 2, tmp.get_metadata_getter_count('acme__fruit__kiwi__1.0') )
      self.assertEqual( 10, tmp.get_metadata('acme__fruit__kiwi__1.0') )
      self.assertEqual( 2, tmp.get_metadata_getter_count('acme__fruit__kiwi__1.0') )

      self.assertEqual( 1, tmp.get_metadata_getter_count('acme__fruit__cherry__2.0') )
      self.assertEqual( 5, tmp.get_metadata('acme__fruit__cherry__2.0') )
      self.assertEqual( 2, tmp.get_metadata_getter_count('acme__fruit__cherry__2.0') )
      self.assertEqual( 5, tmp.get_metadata('acme__fruit__cherry__2.0') )
      self.assertEqual( 2, tmp.get_metadata_getter_count('acme__fruit__cherry__2.0') )

      self.assertEqual( [
        'acme__fruit__cherry__2.0',
        'acme__fruit__kiwi__1.0',
      ], tmp.keys() )

  def test_database_path_basic(self):
    db_path = self.make_temp_file(suffix = '.db', non_existent = True)
    filename = self.make_temp_file(content = b'12345')
    tmp = bf_metadata_file(filename, database_path = db_path)
    self.assertEqual( 5, tmp.get_metadata('acme__fruit__kiwi__1.0') )

  def test_database_path_isolated_from_default(self):
    db_path = self.make_temp_file(suffix = '.db', non_existent = True)
    filename = self.make_temp_file(content = b'12345')
    tmp = bf_metadata_file(filename, database_path = db_path)
    tmp.get_metadata('acme__fruit__kiwi__1.0')
    self.assertTrue( tmp.has_metadata('acme__fruit__kiwi__1.0') )

    tmp_default = bf_metadata_file(filename)
    self.assertFalse( tmp_default.has_metadata('acme__fruit__kiwi__1.0') )

  def test_two_database_paths_are_isolated(self):
    db_path_a = self.make_temp_file(suffix = '.db', non_existent = True)
    db_path_b = self.make_temp_file(suffix = '.db', non_existent = True)
    filename = self.make_temp_file(content = b'12345')
    tmp_a = bf_metadata_file(filename, database_path = db_path_a)
    tmp_b = bf_metadata_file(filename, database_path = db_path_b)
    tmp_a.get_metadata('acme__fruit__kiwi__1.0')
    self.assertTrue( tmp_a.has_metadata('acme__fruit__kiwi__1.0') )
    self.assertFalse( tmp_b.has_metadata('acme__fruit__kiwi__1.0') )

if __name__ == '__main__':
  unit_test.main()

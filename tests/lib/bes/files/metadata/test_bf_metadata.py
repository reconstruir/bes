#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
import time

from bes.files.bf_date import bf_date
from bes.files.attr.bf_attr import bf_attr
from bes.files.metadata.bf_metadata import bf_metadata
from bes.files.metadata.bf_metadata_factory_registry import bf_metadata_factory_registry
from bes.files.metadata.bf_metadata_error import bf_metadata_error
from bes.files.metadata.bf_metadata_file_store import bf_metadata_file_store
from bes.testing.unit_test import unit_test

from _bes_unit_test_common.files.metadata.example_metadata_fruits_factory import example_metadata_fruits_factory

class test_bf_metadata(unit_test):

  def setUp(self):
    db_path = self.make_temp_file(suffix = '.db', non_existent = True)
    bf_metadata._set_file_store(bf_metadata_file_store(database_path = db_path))
    bf_metadata._items.clear()

  def tearDown(self):
    bf_metadata._set_file_store(None)
    bf_metadata._items.clear()

  def test_get_metadata(self):
    tmp = self.make_temp_file(dir = __file__, non_existent = True, suffix = '.data')

    with open(tmp, 'wb') as fout:
      fout.write(b'12345')
      fout.flush()
      os.fsync(fout.fileno())

      self.assertEqual( 0, bf_metadata.get_metadata_getter_count(tmp, 'acme__fruit__kiwi__1.0') )
      self.assertEqual( 0, bf_metadata.get_metadata_getter_count(tmp, 'acme__fruit__kiwi__1.0') )
      self.assertEqual( 5, bf_metadata.get_metadata(tmp, 'acme__fruit__kiwi__1.0') )
      self.assertEqual( 1, bf_metadata.get_metadata_getter_count(tmp, 'acme__fruit__kiwi__1.0') )
      self.assertEqual( 5, bf_metadata.get_metadata(tmp, 'acme__fruit__kiwi__1.0') )
      self.assertEqual( 1, bf_metadata.get_metadata_getter_count(tmp, 'acme__fruit__kiwi__1.0') )
      self.assertEqual( ['acme__fruit__kiwi__1.0'], bf_metadata.keys(tmp) )

      self.assertEqual( 5, bf_metadata.get_metadata(tmp, 'acme__fruit__kiwi__1.0') )
      self.assertEqual( 0, bf_metadata.get_metadata_getter_count(tmp, 'acme__fruit__cherry__2.0') )
      self.assertEqual( 2.5, bf_metadata.get_metadata(tmp, 'acme__fruit__cherry__2.0') )
      self.assertEqual( 1, bf_metadata.get_metadata_getter_count(tmp, 'acme__fruit__cherry__2.0') )
      self.assertEqual( 2.5, bf_metadata.get_metadata(tmp, 'acme__fruit__cherry__2.0') )
      self.assertEqual( 1, bf_metadata.get_metadata_getter_count(tmp, 'acme__fruit__cherry__2.0') )

      self.assertEqual( [
        'acme__fruit__cherry__2.0',
        'acme__fruit__kiwi__1.0',
      ], bf_metadata.keys(tmp) )

      self.assertEqual( 5, bf_metadata.get_metadata(tmp, 'acme__fruit__kiwi__1.0') )
      self.assertEqual( 2.5, bf_metadata.get_metadata(tmp, 'acme__fruit__cherry__2.0') )

      time.sleep(.01)
      fout.seek(0)
      fout.truncate(0)
      fout.write(b'1234567890')
      time.sleep(10.0)
      fout.flush()
      os.fsync(fout.fileno())

      self.assertEqual( 1, bf_metadata.get_metadata_getter_count(tmp, 'acme__fruit__kiwi__1.0') )
      self.assertEqual( 10, bf_metadata.get_metadata(tmp, 'acme__fruit__kiwi__1.0') )
      self.assertEqual( 2, bf_metadata.get_metadata_getter_count(tmp, 'acme__fruit__kiwi__1.0') )
      self.assertEqual( 10, bf_metadata.get_metadata(tmp, 'acme__fruit__kiwi__1.0') )
      self.assertEqual( 2, bf_metadata.get_metadata_getter_count(tmp, 'acme__fruit__kiwi__1.0') )

      self.assertEqual( 1, bf_metadata.get_metadata_getter_count(tmp, 'acme__fruit__cherry__2.0') )
      self.assertEqual( 5, bf_metadata.get_metadata(tmp, 'acme__fruit__cherry__2.0') )
      self.assertEqual( 2, bf_metadata.get_metadata_getter_count(tmp, 'acme__fruit__cherry__2.0') )
      self.assertEqual( 5, bf_metadata.get_metadata(tmp, 'acme__fruit__cherry__2.0') )
      self.assertEqual( 2, bf_metadata.get_metadata_getter_count(tmp, 'acme__fruit__cherry__2.0' ) )

      self.assertEqual( [
        'acme__fruit__cherry__2.0',
        'acme__fruit__kiwi__1.0',
      ], bf_metadata.keys(tmp) )

      self.assertEqual( 10, bf_metadata.get_metadata(tmp, 'acme__fruit__kiwi__1.0') )
      self.assertEqual( 5.0, bf_metadata.get_metadata(tmp, 'acme__fruit__cherry__2.0') )

  def test_get_metadata_old_getter(self):
    tmp = self.make_temp_file(dir = __file__, content = b'1234567890', suffix = '.data')
    mtime = bf_date.get_modification_date(tmp)
    old_key = 'bes_double_size'
    mtime_key = bf_attr.make_mtime_key(old_key)
    bf_metadata.set_date(tmp, mtime_key, mtime)
    bf_metadata.set_int(tmp, old_key, 666)
    bf_date.set_modification_date(tmp, mtime)
    self.assertEqual( 666, bf_metadata.get_metadata(tmp, 'acme__fruit__melon__1.0') )

if __name__ == '__main__':
  unit_test.main()

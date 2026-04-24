#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
import os.path as path

from bes.files.metadata.bf_metadata import bf_metadata
from bes.files.metadata.bf_metadata_file_store import bf_metadata_file_store
from bes.testing.unit_test import unit_test

from _bes_unit_test_common.files.metadata.example_metadata_fruits_factory import example_metadata_fruits_factory

class test_bf_metadata_with_store(unit_test):

  def setUp(self):
    db_path = self.make_temp_file(suffix = '.db', non_existent = True)
    bf_metadata._set_file_store(bf_metadata_file_store(database_path = db_path))
    bf_metadata._items.clear()

  def tearDown(self):
    bf_metadata._set_file_store(None)
    bf_metadata._items.clear()

  def test_get_metadata_basic(self):
    tmp = self.make_temp_file(content = b'12345')
    self.assertEqual( 5, bf_metadata.get_metadata(tmp, 'acme__fruit__kiwi__1.0') )

  def test_get_metadata_cached_in_process(self):
    tmp = self.make_temp_file(content = b'12345')
    self.assertEqual( 0, bf_metadata.get_metadata_getter_count(tmp, 'acme__fruit__kiwi__1.0') )
    bf_metadata.get_metadata(tmp, 'acme__fruit__kiwi__1.0')
    self.assertEqual( 1, bf_metadata.get_metadata_getter_count(tmp, 'acme__fruit__kiwi__1.0') )
    bf_metadata.get_metadata(tmp, 'acme__fruit__kiwi__1.0')
    self.assertEqual( 1, bf_metadata.get_metadata_getter_count(tmp, 'acme__fruit__kiwi__1.0') )

  def test_get_metadata_recomputes_on_content_change(self):
    tmp = self.make_temp_file(content = b'12345')
    self.assertEqual( 5, bf_metadata.get_metadata(tmp, 'acme__fruit__kiwi__1.0') )
    self.assertEqual( 1, bf_metadata.get_metadata_getter_count(tmp, 'acme__fruit__kiwi__1.0') )

    from bes.files.bf_date import bf_date
    import time
    time.sleep(.01)
    with open(tmp, 'wb') as f:
      f.write(b'1234567890')
      f.flush()
      os.fsync(f.fileno())
    time.sleep(10.0)

    self.assertEqual( 10, bf_metadata.get_metadata(tmp, 'acme__fruit__kiwi__1.0') )
    self.assertEqual( 2, bf_metadata.get_metadata_getter_count(tmp, 'acme__fruit__kiwi__1.0') )

  def test_get_metadata_survives_rename(self):
    tmp = self.make_temp_file(content = b'12345')
    self.assertEqual( 5, bf_metadata.get_metadata(tmp, 'acme__fruit__kiwi__1.0') )
    self.assertEqual( 1, bf_metadata.get_metadata_getter_count(tmp, 'acme__fruit__kiwi__1.0') )

    renamed = tmp + '_renamed'
    os.rename(tmp, renamed)
    self.addCleanup(lambda: os.unlink(renamed) if path.exists(renamed) else None)

    bf_metadata._items.clear()
    self.assertEqual( 5, bf_metadata.get_metadata(renamed, 'acme__fruit__kiwi__1.0') )
    self.assertEqual( 1, bf_metadata.get_metadata_getter_count(renamed, 'acme__fruit__kiwi__1.0') )

  def test_has_metadata_true(self):
    tmp = self.make_temp_file(content = b'12345')
    bf_metadata.get_metadata(tmp, 'acme__fruit__kiwi__1.0')
    self.assertTrue( bf_metadata.has_metadata(tmp, 'acme__fruit__kiwi__1.0') )

  def test_has_metadata_false(self):
    tmp = self.make_temp_file(content = b'12345')
    self.assertFalse( bf_metadata.has_metadata(tmp, 'acme__fruit__kiwi__1.0') )

  def test_metadata_delete(self):
    tmp = self.make_temp_file(content = b'12345')
    bf_metadata.get_metadata(tmp, 'acme__fruit__kiwi__1.0')
    self.assertTrue( bf_metadata.has_metadata(tmp, 'acme__fruit__kiwi__1.0') )
    bf_metadata.metadata_delete(tmp, 'acme__fruit__kiwi__1.0')
    self.assertFalse( bf_metadata.has_metadata(tmp, 'acme__fruit__kiwi__1.0') )

  def test_keys_empty(self):
    tmp = self.make_temp_file(content = b'12345')
    self.assertEqual( [], bf_metadata.keys(tmp) )

  def test_keys_after_get(self):
    tmp = self.make_temp_file(content = b'12345')
    bf_metadata.get_metadata(tmp, 'acme__fruit__kiwi__1.0')
    bf_metadata.get_metadata(tmp, 'acme__fruit__cherry__2.0')
    self.assertEqual( [
      'acme__fruit__cherry__2.0',
      'acme__fruit__kiwi__1.0',
    ], bf_metadata.keys(tmp) )

if __name__ == '__main__':
  unit_test.main()

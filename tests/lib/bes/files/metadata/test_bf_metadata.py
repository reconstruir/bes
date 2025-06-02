#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
import time

from bes.docker.docker import docker
from bes.files.bf_date import bf_date
from bes.files.attr.bf_attr import bf_attr
from bes.files.metadata.bf_metadata import bf_metadata
from bes.files.metadata.bf_metadata_factory_registry import bf_metadata_factory_registry
from bes.files.metadata.bf_metadata_error import bf_metadata_error
from bes.testing.unit_test import unit_test

from _bes_unit_test_common.files.metadata.example_metadata_fruits_factory import example_metadata_fruits_factory

class test_bf_metadata(unit_test):

  @classmethod
  def setUpClass(clazz):
    docker.raise_skip_if_running_under_docker()

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
      kiwi_mtime = bf_date.get_modification_date(tmp)
      self.assertEqual( [
        '__bes_mtime_acme__fruit__kiwi__1.0__',
        'acme__fruit__kiwi__1.0',
      ], bf_metadata.keys(tmp) )
      
      self.assertEqual( kiwi_mtime, bf_metadata.get_date(tmp, '__bes_mtime_acme__fruit__kiwi__1.0__') )
      self.assertEqual( 5, bf_metadata.get_metadata(tmp, 'acme__fruit__kiwi__1.0') )
      self.assertEqual( 0, bf_metadata.get_metadata_getter_count(tmp, 'acme__fruit__cherry__2.0') )
      self.assertEqual( 2.5, bf_metadata.get_metadata(tmp, 'acme__fruit__cherry__2.0') )
      self.assertEqual( 1, bf_metadata.get_metadata_getter_count(tmp, 'acme__fruit__cherry__2.0') )
      self.assertEqual( 2.5, bf_metadata.get_metadata(tmp, 'acme__fruit__cherry__2.0') )
      self.assertEqual( 1, bf_metadata.get_metadata_getter_count(tmp, 'acme__fruit__cherry__2.0') )
      cherry_mtime = bf_date.get_modification_date(tmp)

      self.assertEqual( [
        '__bes_mtime_acme__fruit__cherry__2.0__',
        '__bes_mtime_acme__fruit__kiwi__1.0__',
        'acme__fruit__cherry__2.0',
        'acme__fruit__kiwi__1.0',
      ], bf_metadata.keys(tmp) )
      
      self.assertEqual( kiwi_mtime, bf_metadata.get_date(tmp, '__bes_mtime_acme__fruit__kiwi__1.0__') )
      self.assertEqual( 5, bf_metadata.get_metadata(tmp, 'acme__fruit__kiwi__1.0') )
      self.assertEqual( cherry_mtime, bf_metadata.get_date(tmp, '__bes_mtime_acme__fruit__cherry__2.0__') )
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
      kiwi_mtime = bf_date.get_modification_date(tmp)

      self.assertEqual( 1, bf_metadata.get_metadata_getter_count(tmp, 'acme__fruit__cherry__2.0') )
      self.assertEqual( 5, bf_metadata.get_metadata(tmp, 'acme__fruit__cherry__2.0') )
      self.assertEqual( 2, bf_metadata.get_metadata_getter_count(tmp, 'acme__fruit__cherry__2.0') )
      self.assertEqual( 5, bf_metadata.get_metadata(tmp, 'acme__fruit__cherry__2.0') )
      self.assertEqual( 2, bf_metadata.get_metadata_getter_count(tmp, 'acme__fruit__cherry__2.0' ) )
      cherry_mtime = bf_date.get_modification_date(tmp)
      
      self.assertEqual( [
        '__bes_mtime_acme__fruit__cherry__2.0__',
        '__bes_mtime_acme__fruit__kiwi__1.0__',
        'acme__fruit__cherry__2.0',
        'acme__fruit__kiwi__1.0',
      ], bf_metadata.keys(tmp) )

      self.assertEqual( kiwi_mtime, bf_metadata.get_date(tmp, '__bes_mtime_acme__fruit__kiwi__1.0__') )
      self.assertEqual( 10, bf_metadata.get_metadata(tmp, 'acme__fruit__kiwi__1.0') )
      self.assertEqual( cherry_mtime, bf_metadata.get_date(tmp, '__bes_mtime_acme__fruit__cherry__2.0__') )
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

#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
import time

from bes.system.bdocker import bdocker
from bes.files.bf_date import bf_date
from bes.files.metadata.bf_metadata_file import bf_metadata_file
from bes.files.metadata.bf_metadata_factory_registry import bf_metadata_factory_registry
from bes.files.metadata.bf_metadata_error import bf_metadata_error
from bes.testing.unit_test import unit_test

from _bes_unit_test_common.files.metadata.example_metadata_fruits_factory import example_metadata_fruits_factory

class test_bf_metadata_file(unit_test):
  
  @classmethod
  def setUpClass(clazz):
    bdocker.raise_skip_if_running_under_docker()

  def test_get_metadata(self):
    tmp = bf_metadata_file(self.make_temp_file(dir = __file__, non_existent = True, suffix = '.data'))
    
    with open(tmp.filename, 'wb') as fout:
      fout.write(b'12345')
      fout.flush()
      os.fsync(fout.fileno())

      self.assertEqual( 0, tmp.get_metadata_getter_count('acme__fruit__kiwi__1.0') )
      self.assertEqual( 0, tmp.get_metadata_getter_count('acme__fruit__kiwi__1.0') )
      self.assertEqual( 5,  tmp.get_metadata('acme__fruit__kiwi__1.0') )
      self.assertEqual( 1, tmp.get_metadata_getter_count('acme__fruit__kiwi__1.0') )
      self.assertEqual( 5, tmp.get_metadata('acme__fruit__kiwi__1.0') )
      self.assertEqual( 1, tmp.get_metadata_getter_count('acme__fruit__kiwi__1.0') )
      kiwi_mtime = bf_date.get_modification_date(tmp.filename)
      self.assertEqual( [
        '__bes_mtime_acme__fruit__kiwi__1.0__',
        'acme__fruit__kiwi__1.0',
      ], tmp.keys() )
      
      self.assertEqual( kiwi_mtime, tmp.get_date('__bes_mtime_acme__fruit__kiwi__1.0__') )
      self.assertEqual( 5, tmp.get_int('acme__fruit__kiwi__1.0') )
    
      self.assertEqual( 0, tmp.get_metadata_getter_count('acme__fruit__cherry__2.0') )
      self.assertEqual( 2.5, tmp.get_metadata('acme__fruit__cherry__2.0') )
      self.assertEqual( 1, tmp.get_metadata_getter_count('acme__fruit__cherry__2.0') )
      self.assertEqual( 2.5, tmp.get_metadata('acme__fruit__cherry__2.0') )
      self.assertEqual( 1, tmp.get_metadata_getter_count('acme__fruit__cherry__2.0') )
      cherry_mtime = bf_date.get_modification_date(tmp.filename)

      self.assertEqual( [
        '__bes_mtime_acme__fruit__cherry__2.0__',
        '__bes_mtime_acme__fruit__kiwi__1.0__',
        'acme__fruit__cherry__2.0',
        'acme__fruit__kiwi__1.0',
      ], tmp.keys() )
      
      self.assertEqual( kiwi_mtime, tmp.get_date('__bes_mtime_acme__fruit__kiwi__1.0__') )
      self.assertEqual( 5, tmp.get_int('acme__fruit__kiwi__1.0') )
      self.assertEqual( cherry_mtime, tmp.get_date('__bes_mtime_acme__fruit__cherry__2.0__') )
      self.assertEqual( 2.5, tmp.get_float('acme__fruit__cherry__2.0') )

      time.sleep(.01)
      fout.seek(0)
      fout.truncate(0)
      fout.write(b'1234567890')
      fout.flush()
      os.fsync(fout.fileno())

      self.assertEqual( 1, tmp.get_metadata_getter_count('acme__fruit__kiwi__1.0') )
      self.assertEqual( 10, tmp.get_metadata('acme__fruit__kiwi__1.0') )
      self.assertEqual( 2, tmp.get_metadata_getter_count('acme__fruit__kiwi__1.0') )
      self.assertEqual( 10, tmp.get_metadata('acme__fruit__kiwi__1.0') )
      self.assertEqual( 2, tmp.get_metadata_getter_count('acme__fruit__kiwi__1.0') )
      kiwi_mtime = bf_date.get_modification_date(tmp.filename)

      self.assertEqual( 1, tmp.get_metadata_getter_count('acme__fruit__cherry__2.0') )
      self.assertEqual( 5, tmp.get_metadata('acme__fruit__cherry__2.0') )
      self.assertEqual( 2, tmp.get_metadata_getter_count('acme__fruit__cherry__2.0') )
      self.assertEqual( 5, tmp.get_metadata('acme__fruit__cherry__2.0') )
      self.assertEqual( 2, tmp.get_metadata_getter_count('acme__fruit__cherry__2.0' ) )
      cherry_mtime = bf_date.get_modification_date(tmp.filename)
      
      self.assertEqual( [
        '__bes_mtime_acme__fruit__cherry__2.0__',
        '__bes_mtime_acme__fruit__kiwi__1.0__',
        'acme__fruit__cherry__2.0',
        'acme__fruit__kiwi__1.0',
      ], tmp.keys() )

      self.assertEqual( kiwi_mtime, tmp.get_date('__bes_mtime_acme__fruit__kiwi__1.0__') )
      self.assertEqual( 10, tmp.get_int('acme__fruit__kiwi__1.0') )
      self.assertEqual( cherry_mtime, tmp.get_date('__bes_mtime_acme__fruit__cherry__2.0__') )
      self.assertEqual( 5, tmp.get_float('acme__fruit__cherry__2.0') )

if __name__ == '__main__':
  unit_test.main()

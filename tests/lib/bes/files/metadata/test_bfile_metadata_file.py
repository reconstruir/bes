#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
import time

from bes.docker.docker import docker
from bes.files.bfile_date import bfile_date
from bes.files.metadata.bfile_metadata_file import bfile_metadata_file
from bes.files.metadata.bfile_metadata_factory_registry import bfile_metadata_factory_registry
from bes.files.metadata.bfile_metadata_error import bfile_metadata_error
from bes.testing.unit_test import unit_test

from _test_fruits_factory import _test_fruits_factory

class test_bfile_metadata_file(unit_test):
  
  @classmethod
  def setUpClass(clazz):
    docker.raise_skip_if_running_under_docker()
    bfile_metadata_factory_registry.unregister_factory(_test_fruits_factory)
    bfile_metadata_factory_registry.register_factory(_test_fruits_factory)

  @classmethod
  def tearDownClass(clazz):
    bfile_metadata_factory_registry.unregister_factory(_test_fruits_factory)

  def test_get_metadata(self):
    tmp = bfile_metadata_file(self.make_temp_file(dir = __file__, non_existent = True, suffix = '.data'))
    
    with open(tmp.filename, 'wb') as fout:
      fout.write(b'12345')
      fout.flush()
      os.fsync(fout.fileno())

      self.assertEqual( 0, tmp.get_metadata_getter_count('acme/fruit/kiwi/1.0') )
      self.assertEqual( 0, tmp.get_metadata_getter_count('acme/fruit/kiwi/1.0') )
      self.assertEqual( 5,  tmp.get_metadata('acme/fruit/kiwi/1.0') )
      self.assertEqual( 1, tmp.get_metadata_getter_count('acme/fruit/kiwi/1.0') )
      self.assertEqual( 5, tmp.get_metadata('acme/fruit/kiwi/1.0') )
      self.assertEqual( 1, tmp.get_metadata_getter_count('acme/fruit/kiwi/1.0') )
      kiwi_mtime = bfile_date.get_modification_date(tmp.filename)
      self.assertEqual( [
        '__bes_mtime_acme/fruit/kiwi/1.0__',
        'acme/fruit/kiwi/1.0',
      ], tmp.keys() )
      
      self.assertEqual( kiwi_mtime, tmp.get_date('__bes_mtime_acme/fruit/kiwi/1.0__') )
      self.assertEqual( 5, tmp.get_int('acme/fruit/kiwi/1.0') )
    
      self.assertEqual( 0, tmp.get_metadata_getter_count('acme/fruit/cherry/2.0') )
      self.assertEqual( 2.5, tmp.get_metadata('acme/fruit/cherry/2.0') )
      self.assertEqual( 1, tmp.get_metadata_getter_count('acme/fruit/cherry/2.0') )
      self.assertEqual( 2.5, tmp.get_metadata('acme/fruit/cherry/2.0') )
      self.assertEqual( 1, tmp.get_metadata_getter_count('acme/fruit/cherry/2.0') )
      cherry_mtime = bfile_date.get_modification_date(tmp.filename)

      self.assertEqual( [
        '__bes_mtime_acme/fruit/cherry/2.0__',
        '__bes_mtime_acme/fruit/kiwi/1.0__',
        'acme/fruit/cherry/2.0',
        'acme/fruit/kiwi/1.0',
      ], tmp.keys() )
      
      self.assertEqual( kiwi_mtime, tmp.get_date('__bes_mtime_acme/fruit/kiwi/1.0__') )
      self.assertEqual( 5, tmp.get_int('acme/fruit/kiwi/1.0') )
      self.assertEqual( cherry_mtime, tmp.get_date('__bes_mtime_acme/fruit/cherry/2.0__') )
      self.assertEqual( 2.5, tmp.get_float('acme/fruit/cherry/2.0') )

      time.sleep(.01)
      fout.seek(0)
      fout.truncate(0)
      fout.write(b'1234567890')
      fout.flush()
      os.fsync(fout.fileno())

      self.assertEqual( 1, tmp.get_metadata_getter_count('acme/fruit/kiwi/1.0') )
      self.assertEqual( 10, tmp.get_metadata('acme/fruit/kiwi/1.0') )
      self.assertEqual( 2, tmp.get_metadata_getter_count('acme/fruit/kiwi/1.0') )
      self.assertEqual( 10, tmp.get_metadata('acme/fruit/kiwi/1.0') )
      self.assertEqual( 2, tmp.get_metadata_getter_count('acme/fruit/kiwi/1.0') )
      kiwi_mtime = bfile_date.get_modification_date(tmp.filename)

      self.assertEqual( 1, tmp.get_metadata_getter_count('acme/fruit/cherry/2.0') )
      self.assertEqual( 5, tmp.get_metadata('acme/fruit/cherry/2.0') )
      self.assertEqual( 2, tmp.get_metadata_getter_count('acme/fruit/cherry/2.0') )
      self.assertEqual( 5, tmp.get_metadata('acme/fruit/cherry/2.0') )
      self.assertEqual( 2, tmp.get_metadata_getter_count('acme/fruit/cherry/2.0' ) )
      cherry_mtime = bfile_date.get_modification_date(tmp.filename)
      
      self.assertEqual( [
        '__bes_mtime_acme/fruit/cherry/2.0__',
        '__bes_mtime_acme/fruit/kiwi/1.0__',
        'acme/fruit/cherry/2.0',
        'acme/fruit/kiwi/1.0',
      ], tmp.keys() )

      self.assertEqual( kiwi_mtime, tmp.get_date('__bes_mtime_acme/fruit/kiwi/1.0__') )
      self.assertEqual( 10, tmp.get_int('acme/fruit/kiwi/1.0') )
      self.assertEqual( cherry_mtime, tmp.get_date('__bes_mtime_acme/fruit/cherry/2.0__') )
      self.assertEqual( 5, tmp.get_float('acme/fruit/cherry/2.0') )

  def test_set_metadata(self):
    tmp = bfile_metadata_file(self.make_temp_file(dir = __file__, content = b'12345', suffix = '.data'))

    self.assertEqual( None,  tmp.get_metadata('acme/fruit/price/1.0') )
    self.assertEqual( [], tmp.keys() )
    tmp.set_metadata('acme/fruit/price/1.0', 666)
    self.assertEqual( [ 'acme/fruit/price/1.0' ], tmp.keys() )
    self.assertEqual( 0, tmp.get_metadata_getter_count('acme/fruit/price/1.0') )
    self.assertEqual( 666, tmp.get_metadata('acme/fruit/price/1.0') )
    self.assertEqual( 1, tmp.get_metadata_getter_count('acme/fruit/price/1.0') )
    self.assertEqual( 666, tmp.get_metadata('acme/fruit/price/1.0') )
    self.assertEqual( 1, tmp.get_metadata_getter_count('acme/fruit/price/1.0') )
    self.assertEqual( [
      '__bes_mtime_acme/fruit/price/1.0__',
      'acme/fruit/price/1.0',
    ], tmp.keys() )
    tmp.set_metadata('acme/fruit/price/1.0', 42)
    self.assertEqual( 42, tmp.get_int('acme/fruit/price/1.0') )
    self.assertEqual( [
      'acme/fruit/price/1.0',
    ], tmp.keys() )
    self.assertEqual( 42, tmp.get_metadata('acme/fruit/price/1.0') )
    self.assertEqual( 2, tmp.get_metadata_getter_count('acme/fruit/price/1.0') )
    kiwi_mtime = bfile_date.get_modification_date(tmp.filename)
    self.assertEqual( [
      '__bes_mtime_acme/fruit/price/1.0__',
      'acme/fruit/price/1.0',
    ], tmp.keys() )
    self.assertEqual( kiwi_mtime, tmp.get_date('__bes_mtime_acme/fruit/price/1.0__') )
    self.assertEqual( 42, tmp.get_metadata('acme/fruit/price/1.0') )
    #self.assertEqual( 3, tmp.get_metadata_getter_count('acme/fruit/price/1.0') )

  def test_set_metadata_read_only(self):
    tmp = bfile_metadata_file(self.make_temp_file(dir = __file__, content = b'12345', suffix = '.data'))
    with self.assertRaises(bfile_metadata_error) as ex:
      tmp.set_metadata('acme/fruit/cherry/2.0', 666)
    
if __name__ == '__main__':
  unit_test.main()

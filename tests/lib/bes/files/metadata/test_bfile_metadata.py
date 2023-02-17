#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
import time

from bes.docker.docker import docker
from bes.files.bfile_date import bfile_date
from bes.files.metadata.bfile_metadata import bfile_metadata
from bes.files.metadata.bfile_metadata_factory_registry import bfile_metadata_factory_registry
from bes.files.metadata.bfile_metadata_error import bfile_metadata_error
from bes.testing.unit_test import unit_test

from _test_fruits_factory import _test_fruits_factory

class test_bfile_metadata(unit_test):

  @classmethod
  def setUpClass(clazz):
    docker.raise_skip_if_running_under_docker()
    bfile_metadata_factory_registry.unregister_factory(_test_fruits_factory)
    bfile_metadata_factory_registry.register_factory(_test_fruits_factory)

  @classmethod
  def tearDownClass(clazz):
    bfile_metadata_factory_registry.unregister_factory(_test_fruits_factory)

  def test_get_metadata(self):
    tmp = self.make_temp_file(dir = __file__, non_existent = True, suffix = '.data')

    with open(tmp, 'wb') as fout:
      fout.write(b'12345')
      fout.flush()
      os.fsync(fout.fileno())

      self.assertEqual( 0, bfile_metadata.get_metadata_getter_count(tmp, 'acme/fruit/kiwi/1.0') )
      self.assertEqual( 0, bfile_metadata.get_metadata_getter_count(tmp, 'acme/fruit/kiwi/1.0') )
      self.assertEqual( 5, bfile_metadata.get_metadata(tmp, 'acme/fruit/kiwi/1.0') )
      self.assertEqual( 1, bfile_metadata.get_metadata_getter_count(tmp, 'acme/fruit/kiwi/1.0') )
      self.assertEqual( 5, bfile_metadata.get_metadata(tmp, 'acme/fruit/kiwi/1.0') )
      self.assertEqual( 1, bfile_metadata.get_metadata_getter_count(tmp, 'acme/fruit/kiwi/1.0') )
      kiwi_mtime = bfile_date.get_modification_date(tmp)
      self.assertEqual( [
        '__bes_mtime_acme/fruit/kiwi/1.0__',
        'acme/fruit/kiwi/1.0',
      ], bfile_metadata.keys(tmp) )
      
      self.assertEqual( kiwi_mtime, bfile_metadata.get_date(tmp, '__bes_mtime_acme/fruit/kiwi/1.0__') )
      self.assertEqual( 5, bfile_metadata.get_metadata(tmp, 'acme/fruit/kiwi/1.0') )
      self.assertEqual( 0, bfile_metadata.get_metadata_getter_count(tmp, 'acme/fruit/cherry/2.0') )
      self.assertEqual( 2.5, bfile_metadata.get_metadata(tmp, 'acme/fruit/cherry/2.0') )
      self.assertEqual( 1, bfile_metadata.get_metadata_getter_count(tmp, 'acme/fruit/cherry/2.0') )
      self.assertEqual( 2.5, bfile_metadata.get_metadata(tmp, 'acme/fruit/cherry/2.0') )
      self.assertEqual( 1, bfile_metadata.get_metadata_getter_count(tmp, 'acme/fruit/cherry/2.0') )
      cherry_mtime = bfile_date.get_modification_date(tmp)

      self.assertEqual( [
        '__bes_mtime_acme/fruit/cherry/2.0__',
        '__bes_mtime_acme/fruit/kiwi/1.0__',
        'acme/fruit/cherry/2.0',
        'acme/fruit/kiwi/1.0',
      ], bfile_metadata.keys(tmp) )
      
      self.assertEqual( kiwi_mtime, bfile_metadata.get_date(tmp, '__bes_mtime_acme/fruit/kiwi/1.0__') )
      self.assertEqual( 5, bfile_metadata.get_metadata(tmp, 'acme/fruit/kiwi/1.0') )
      self.assertEqual( cherry_mtime, bfile_metadata.get_date(tmp, '__bes_mtime_acme/fruit/cherry/2.0__') )
      self.assertEqual( 2.5, bfile_metadata.get_metadata(tmp, 'acme/fruit/cherry/2.0') )

      time.sleep(.01)
      fout.seek(0)
      fout.truncate(0)
      fout.write(b'1234567890')
      fout.flush()
      os.fsync(fout.fileno())

      self.assertEqual( 1, bfile_metadata.get_metadata_getter_count(tmp, 'acme/fruit/kiwi/1.0') )
      self.assertEqual( 10, bfile_metadata.get_metadata(tmp, 'acme/fruit/kiwi/1.0') )
      self.assertEqual( 2, bfile_metadata.get_metadata_getter_count(tmp, 'acme/fruit/kiwi/1.0') )
      self.assertEqual( 10, bfile_metadata.get_metadata(tmp, 'acme/fruit/kiwi/1.0') )
      self.assertEqual( 2, bfile_metadata.get_metadata_getter_count(tmp, 'acme/fruit/kiwi/1.0') )
      kiwi_mtime = bfile_date.get_modification_date(tmp)

      self.assertEqual( 1, bfile_metadata.get_metadata_getter_count(tmp, 'acme/fruit/cherry/2.0') )
      self.assertEqual( 5, bfile_metadata.get_metadata(tmp, 'acme/fruit/cherry/2.0') )
      self.assertEqual( 2, bfile_metadata.get_metadata_getter_count(tmp, 'acme/fruit/cherry/2.0') )
      self.assertEqual( 5, bfile_metadata.get_metadata(tmp, 'acme/fruit/cherry/2.0') )
      self.assertEqual( 2, bfile_metadata.get_metadata_getter_count(tmp, 'acme/fruit/cherry/2.0' ) )
      cherry_mtime = bfile_date.get_modification_date(tmp)
      
      self.assertEqual( [
        '__bes_mtime_acme/fruit/cherry/2.0__',
        '__bes_mtime_acme/fruit/kiwi/1.0__',
        'acme/fruit/cherry/2.0',
        'acme/fruit/kiwi/1.0',
      ], bfile_metadata.keys(tmp) )

      self.assertEqual( kiwi_mtime, bfile_metadata.get_date(tmp, '__bes_mtime_acme/fruit/kiwi/1.0__') )
      self.assertEqual( 10, bfile_metadata.get_metadata(tmp, 'acme/fruit/kiwi/1.0') )
      self.assertEqual( cherry_mtime, bfile_metadata.get_date(tmp, '__bes_mtime_acme/fruit/cherry/2.0__') )
      self.assertEqual( 5.0, bfile_metadata.get_metadata(tmp, 'acme/fruit/cherry/2.0') )

  def test_set_metadata(self):
    tmp = self.make_temp_file(dir = __file__, content = b'12345', suffix = '.data')

    self.assertEqual( None,  bfile_metadata.get_metadata(tmp, 'acme/fruit/price/1.0') )
    self.assertEqual( [], bfile_metadata.keys(tmp) )
    bfile_metadata.set_metadata(tmp, 'acme/fruit/price/1.0', 666)
    self.assertEqual( [ 'acme/fruit/price/1.0' ], bfile_metadata.keys(tmp) )
    self.assertEqual( 0, bfile_metadata.get_metadata_getter_count(tmp, 'acme/fruit/price/1.0') )
    self.assertEqual( 666, bfile_metadata.get_metadata(tmp, 'acme/fruit/price/1.0') )
    self.assertEqual( 1, bfile_metadata.get_metadata_getter_count(tmp, 'acme/fruit/price/1.0') )
    self.assertEqual( 666, bfile_metadata.get_metadata(tmp, 'acme/fruit/price/1.0') )
    self.assertEqual( 1, bfile_metadata.get_metadata_getter_count(tmp, 'acme/fruit/price/1.0') )
    self.assertEqual( [
      '__bes_mtime_acme/fruit/price/1.0__',
      'acme/fruit/price/1.0',
    ], bfile_metadata.keys(tmp) )
    bfile_metadata.set_metadata(tmp, 'acme/fruit/price/1.0', 42)
    self.assertEqual( 42, bfile_metadata.get_int(tmp, 'acme/fruit/price/1.0') )
    self.assertEqual( [
      'acme/fruit/price/1.0',
    ], bfile_metadata.keys(tmp) )
    self.assertEqual( 42, bfile_metadata.get_metadata(tmp, 'acme/fruit/price/1.0') )
    self.assertEqual( 2, bfile_metadata.get_metadata_getter_count(tmp, 'acme/fruit/price/1.0') )
    kiwi_mtime = bfile_date.get_modification_date(tmp)
    self.assertEqual( [
      '__bes_mtime_acme/fruit/price/1.0__',
      'acme/fruit/price/1.0',
    ], bfile_metadata.keys(tmp) )
    self.assertEqual( kiwi_mtime, bfile_metadata.get_date(tmp, '__bes_mtime_acme/fruit/price/1.0__') )
    self.assertEqual( 42, bfile_metadata.get_metadata(tmp, 'acme/fruit/price/1.0') )
    #self.assertEqual( 3, bfile_metadata.get_metadata_getter_count(tmp, 'acme/fruit/price/1.0') )

  def test_set_metadata_read_only(self):
    tmp = self.make_temp_file(dir = __file__, content = b'12345', suffix = '.data')
    with self.assertRaises(bfile_metadata_error) as ex:
      bfile_metadata.set_metadata(tmp, 'acme/fruit/cherry/2.0', 666)
    
if __name__ == '__main__':
  unit_test.main()

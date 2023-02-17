#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
import time

from bes.docker.docker import docker
from bes.files.bfile_date import bfile_date
from bes.files.metadata.bfile_metadata import bfile_metadata
from bes.files.metadata.bfile_metadata_poto import bfile_metadata_poto
from bes.files.metadata.bfile_metadata_factory_base import bfile_metadata_factory_base
from bes.files.metadata.bfile_metadata_factory_registry import bfile_metadata_factory_registry
from bes.testing.unit_test import unit_test

class test_bfile_metadata_poto(unit_test):

  class _test_fruits_factory(bfile_metadata_factory_base):
      
    @classmethod
    #@abstractmethod
    def handlers(clazz):
      return [
        ( 'acme/fruit/kiwi/1.0', clazz._get_kiwi_1_0, clazz.decode_int, None ),
        ( 'acme/fruit/cherry/2.0', clazz._get_cherry_2_0, clazz.decode_float, None ),
        ( 'acme/fruit/price/1.0', None, clazz.decode_int, clazz.encode_int ),
      ]

    @classmethod
    def _get_kiwi_1_0(clazz, filename):
      return clazz.encode_int(os.stat(filename).st_size)

    @classmethod
    def _get_cherry_2_0(clazz, filename):
      return clazz.encode_float(os.stat(filename).st_size / 2.0)
  
  @classmethod
  def setUpClass(clazz):
    docker.raise_skip_if_running_under_docker()
    bfile_metadata_factory_registry.register_factory(clazz._test_fruits_factory)

  @classmethod
  def tearDownClass(clazz):
    bfile_metadata_factory_registry.unregister_factory(clazz._test_fruits_factory)

  def test___getitem__(self):
    tmp = self.make_temp_file(dir = __file__, non_existent = True, suffix = '.data')
    tmp_poto = bfile_metadata_poto(tmp)

    with open(tmp, 'wb') as fout:
      fout.write(b'12345')
      fout.flush()
      os.fsync(fout.fileno())

      self.assertEqual( 0, bfile_metadata.get_metadata_getter_count(tmp, 'acme/fruit/kiwi/1.0') )
      self.assertEqual( 5, tmp_poto['acme/fruit/kiwi/1.0'] )
      self.assertEqual( 1, bfile_metadata.get_metadata_getter_count(tmp, 'acme/fruit/kiwi/1.0') )
      self.assertEqual( 5, tmp_poto['acme/fruit/kiwi/1.0'] )
      self.assertEqual( 1, bfile_metadata.get_metadata_getter_count(tmp, 'acme/fruit/kiwi/1.0') )
      kiwi_mtime = bfile_date.get_modification_date(tmp)
      self.assertEqual( [
        '__bes_mtime_acme/fruit/kiwi/1.0__',
        'acme/fruit/kiwi/1.0',
      ], bfile_metadata.keys(tmp) )
      
      self.assertEqual( kiwi_mtime, bfile_metadata.get_date(tmp, '__bes_mtime_acme/fruit/kiwi/1.0__') )
      self.assertEqual( 5, tmp_poto['acme/fruit/kiwi/1.0'] )
    
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
      self.assertEqual( 5, tmp_poto['acme/fruit/kiwi/1.0'] )
      self.assertEqual( cherry_mtime, bfile_metadata.get_date(tmp, '__bes_mtime_acme/fruit/cherry/2.0__') )
      self.assertEqual( 2.5, tmp_poto['acme/fruit/cherry/2.0'] )

      time.sleep(.01)
      fout.seek(0)
      fout.truncate(0)
      fout.write(b'1234567890')
      fout.flush()
      os.fsync(fout.fileno())

      self.assertEqual( 1, bfile_metadata.get_metadata_getter_count(tmp, 'acme/fruit/kiwi/1.0') )
      self.assertEqual( 10, tmp_poto['acme/fruit/kiwi/1.0'] )
      self.assertEqual( 2, bfile_metadata.get_metadata_getter_count(tmp, 'acme/fruit/kiwi/1.0') )
      self.assertEqual( 10, tmp_poto['acme/fruit/kiwi/1.0'] )
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
      self.assertEqual( 10, tmp_poto['acme/fruit/kiwi/1.0'] )
      self.assertEqual( cherry_mtime, bfile_metadata.get_date(tmp, '__bes_mtime_acme/fruit/cherry/2.0__') )
      self.assertEqual( 5.0, tmp_poto['acme/fruit/cherry/2.0'] )
      
if __name__ == '__main__':
  unit_test.main()

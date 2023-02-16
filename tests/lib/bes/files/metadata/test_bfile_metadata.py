#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os

from bes.docker.docker import docker
from bes.files.bfile_date import bfile_date
from bes.files.metadata.bfile_metadata import bfile_metadata
from bes.files.metadata.bfile_metadata_factory_base import bfile_metadata_factory_base
from bes.files.metadata.bfile_metadata_factory_registry import bfile_metadata_factory_registry
from bes.testing.unit_test import unit_test

class test_bfile_metadata(unit_test):

  class _test_fruits_factory(bfile_metadata_factory_base):
      
    @classmethod
    #@abstractmethod
    def handlers(clazz):
      return [
        ( 'acme', 'fruit', 'kiwi', '1.0', clazz._get_kiwi_1_0, clazz._decode_kiwi_1_0, False ),
        ( 'acme', 'fruit', 'cherry', '2.0', clazz._get_cherry_2_0, clazz._decode_cherry_2_0, False ),
      ]

    _kiwi_1_0_count = 0
    @classmethod
    def _get_kiwi_1_0(clazz, filename):
      clazz._kiwi_1_0_count += 1
      return clazz.encode_int(os.stat(filename).st_size)

    @classmethod
    def _decode_kiwi_1_0(clazz, value):
      return clazz.decode_int(value)
      
    _cherry_2_0_count = 0
    @classmethod
    def _get_cherry_2_0(clazz, filename):
      clazz._cherry_2_0_count += 1
      return clazz.encode_float(os.stat(filename).st_size / 2.0)

    @classmethod
    def _decode_cherry_2_0(clazz, value):
      return clazz.decode_float(value)
  
  @classmethod
  def setUpClass(clazz):
    docker.raise_skip_if_running_under_docker()
    bfile_metadata_factory_registry.register_factory(clazz._test_fruits_factory)

  @classmethod
  def tearDownClass(clazz):
    bfile_metadata_factory_registry.unregister_factory(clazz._test_fruits_factory)

  def test_get_metadata(self):
    tmp = self.make_temp_file(dir = __file__, content = b'12345', suffix = '.data')

    self.assertEqual( 0, self._test_fruits_factory._kiwi_1_0_count )
    #self.assertEqual( 0, impl.get_metadata_getter_count('acme', 'fruit', 'kiwi', '1.0') )
    self.assertEqual( 5,  bfile_metadata.get_metadata(tmp, 'acme', 'fruit', 'kiwi', '1.0') )
    self.assertEqual( 1, self._test_fruits_factory._kiwi_1_0_count )
    self.assertEqual( 5, bfile_metadata.get_metadata(tmp, 'acme', 'fruit', 'kiwi', '1.0') )
    self.assertEqual( 1, self._test_fruits_factory._kiwi_1_0_count )
    kiwi_mtime = bfile_date.get_modification_date(tmp)

    self.assertEqual( 0, self._test_fruits_factory._cherry_2_0_count )
    self.assertEqual( 2.5, bfile_metadata.get_metadata(tmp, 'acme', 'fruit', 'cherry', '2.0') )
    self.assertEqual( 1, self._test_fruits_factory._cherry_2_0_count )
    self.assertEqual( 2.5, bfile_metadata.get_metadata(tmp, 'acme', 'fruit', 'cherry', '2.0') )
    self.assertEqual( 1, self._test_fruits_factory._cherry_2_0_count )
    cherry_mtime = bfile_date.get_modification_date(tmp)

    self.assertEqual( {
      '__bes_mtime_acme/fruit/cherry/2.0__': str(cherry_mtime.timestamp()).encode('utf-8'),
      '__bes_mtime_acme/fruit/kiwi/1.0__': str(kiwi_mtime.timestamp()).encode('utf-8'),
      'acme/fruit/cherry/2.0': b'2.5',
      'acme/fruit/kiwi/1.0': b'5',
    }, bfile_metadata.get_all(tmp) )
      
    with open(tmp, 'wb') as f:
      f.write(b'1234567890')
      f.flush()

    self.assertEqual( 1, self._test_fruits_factory._kiwi_1_0_count )
    self.assertEqual( 10, bfile_metadata.get_metadata(tmp, 'acme', 'fruit', 'kiwi', '1.0') )
    self.assertEqual( 2, self._test_fruits_factory._kiwi_1_0_count )
    self.assertEqual( 10, bfile_metadata.get_metadata(tmp, 'acme', 'fruit', 'kiwi', '1.0') )
    self.assertEqual( 2, self._test_fruits_factory._kiwi_1_0_count )
    kiwi_mtime = bfile_date.get_modification_date(tmp)

    self.assertEqual( {
      '__bes_mtime_acme/fruit/cherry/2.0__': str(cherry_mtime.timestamp()).encode('utf-8'),
      '__bes_mtime_acme/fruit/kiwi/1.0__': str(kiwi_mtime.timestamp()).encode('utf-8'),
      'acme/fruit/cherry/2.0': b'2.5',
      'acme/fruit/kiwi/1.0': b'10',
    }, bfile_metadata.get_all(tmp) )
      
    with open(tmp, 'wb') as f:
      f.write(b'12')
      f.flush()
      
    self.assertEqual( 1, self._test_fruits_factory._cherry_2_0_count )
    self.assertEqual( 1, bfile_metadata.get_metadata(tmp, 'acme', 'fruit', 'cherry', '2.0') )
    self.assertEqual( 2, self._test_fruits_factory._cherry_2_0_count )
    self.assertEqual( 1, bfile_metadata.get_metadata(tmp, 'acme', 'fruit', 'cherry', '2.0') )
    self.assertEqual( 2, self._test_fruits_factory._cherry_2_0_count )
    cherry_mtime = bfile_date.get_modification_date(tmp)

    self.assertEqual( {
      '__bes_mtime_acme/fruit/cherry/2.0__': str(cherry_mtime.timestamp()).encode('utf-8'),
      '__bes_mtime_acme/fruit/kiwi/1.0__': str(kiwi_mtime.timestamp()).encode('utf-8'),
      'acme/fruit/cherry/2.0': b'1.0',
      'acme/fruit/kiwi/1.0': b'10',
    }, bfile_metadata.get_all(tmp) )
    
if __name__ == '__main__':
  unit_test.main()

#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.files.metadata.bfile_metadata_factory_registry import bfile_metadata_factory_registry
from bes.files.metadata.bfile_metadata_factory_base import bfile_metadata_factory_base

class test_bfile_metadata_factory_registry(unit_test):

  class _test_fruits_factory(bfile_metadata_factory_base):
      
    @classmethod
    #@abstractmethod
    def handlers(clazz):
      return [
        ( 'acme/fruit/kiwi/1.0', clazz._get_kiwi_1_0, clazz._decode_kiwi_1_0, None ),
        ( 'acme/fruit/cherry/2.0', clazz._get_cherry_2_0, clazz._decode_cherry_2_0, None ),
      ]

    @classmethod
    def _get_kiwi_1_0(clazz, filename):
      return clazz.encode_int(os.stat(filename).st_size)

    @classmethod
    def _decode_kiwi_1_0(clazz, value):
      return clazz.decode_int(value)
        
    @classmethod
    def _get_cherry_2_0(clazz, filename):
      return clazz.encode_float(os.stat(filename).st_size / 2.0)

    @classmethod
    def _decode_cherry_2_0(clazz, value):
      return clazz.decode_float(value)
  
  @classmethod
  def setUpClass(clazz):
    bfile_metadata_factory_registry.register_factory(clazz._test_fruits_factory)

  @classmethod
  def tearDownClass(clazz):
    bfile_metadata_factory_registry.unregister_factory(clazz._test_fruits_factory)
  
  def test_register_attr_factory(self):
    self.assertEqual( True, bfile_metadata_factory_registry.has_handler('acme/fruit/kiwi/1.0') )
    self.assertEqual( False, bfile_metadata_factory_registry.has_handler('acme/fruit/kiwi/2.0') )
    self.assertEqual( False, bfile_metadata_factory_registry.has_handler('acme/fruit/cherry/1.0') )
    self.assertEqual( True, bfile_metadata_factory_registry.has_handler('acme/fruit/cherry/2.0') )
                                                                    
if __name__ == '__main__':
  unit_test.main()

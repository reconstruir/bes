#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.files.attributes.bfile_attr_factory_registry import bfile_attr_factory_registry
from bes.files.attributes.bfile_attr_factory_base import bfile_attr_factory_base

class test_bfile_attr_factory_registry(unit_test):
  
  def test_register_attr_factory(self):
    class _test_fruits_factory(bfile_attr_factory_base):
      
      @classmethod
      #@abstractmethod
      def handlers(clazz):
        return [
          ( 'fruit', 'kiwi', '1.0', clazz._get_kiwi_1_0, clazz._decode_kiwi_1_0, False ),
          ( 'fruit', 'cherry', '2.0', clazz._get_cherry_2_0, clazz._decode_cherry_2_0, False ),
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
        
    bfile_attr_factory_registry.register_factory(_test_fruits_factory)
    self.assertEqual( True, bfile_attr_factory_registry.has_handler('fruit', 'kiwi', '1.0') )
    self.assertEqual( False, bfile_attr_factory_registry.has_handler('fruit', 'kiwi', '2.0') )
    self.assertEqual( False, bfile_attr_factory_registry.has_handler('fruit', 'cherry', '1.0') )
    self.assertEqual( True, bfile_attr_factory_registry.has_handler('fruit', 'cherry', '2.0') )
    bfile_attr_factory_registry.clear_all()
                                                                    
if __name__ == '__main__':
  unit_test.main()

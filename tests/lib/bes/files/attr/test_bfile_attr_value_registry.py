#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test

from bes.files.attr.bfile_attr_error import bfile_attr_error
from bes.files.attr.bfile_attr_value_factory_base import bfile_attr_value_factory_base
from bes.files.attr.bfile_attr_value_registry import bfile_attr_value_registry

from _bes_unit_test_common.files.attr.fruits_factory import fruits_factory

class test_bfile_attr_value_registry(unit_test):

  @classmethod
  def setUpClass(clazz):
    bfile_attr_value_registry.unregister_factory(fruits_factory)
    bfile_attr_value_registry.register_factory(fruits_factory)

  @classmethod
  def tearDownClass(clazz):
    bfile_attr_value_registry.unregister_factory(fruits_factory)
  
  def test_register_attr_value_handler_factory(self):
    self.assertEqual( True, bfile_attr_value_registry.has_value('acme/fruit/kiwi/1.0') )
    self.assertEqual( False, bfile_attr_value_registry.has_value('acme/fruit/kiwi/2.0') )
    self.assertEqual( False, bfile_attr_value_registry.has_value('acme/fruit/cherry/1.0') )
    self.assertEqual( True, bfile_attr_value_registry.has_value('acme/fruit/cherry/2.0') )

  def test_register_factory_duplicate(self):
    class _kiwi1_factory(bfile_attr_value_factory_base):
      @classmethod
      #@abstractmethod
      def descriptions(clazz):
        return [
          ( 'kiwi', lambda v: 1, lambda v: b'1', lambda v: v, None ),
        ]
    with self.assertRaises(bfile_attr_error) as ctx:
      class _kiwi2_factory(bfile_attr_value_factory_base):
        @classmethod
        #@abstractmethod
        def descriptions(clazz):
          return [
            ( 'kiwi', lambda v: 2, lambda v: b'2', lambda v: v, None ),
          ]
    bfile_attr_value_registry.unregister_factory(_kiwi1_factory)
    
  def test_register_factory_duplicate_same_descriptions(self):
    class _kiwi_factory(bfile_attr_value_factory_base):
      @classmethod
      #@abstractmethod
      def descriptions(clazz):
        return [
          ( 'kiwi', lambda v: 1, lambda v: b'1', lambda v: v, None ),
        ]
    bfile_attr_value_registry.register_factory(_kiwi_factory)
    bfile_attr_value_registry.register_factory(_kiwi_factory)
    bfile_attr_value_registry.unregister_factory(_kiwi_factory)
    
if __name__ == '__main__':
  unit_test.main()

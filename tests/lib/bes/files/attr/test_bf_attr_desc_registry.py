#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test

from bes.files.attr.bf_attr_error import bf_attr_error
from bes.files.attr.bf_attr_desc_factory_base import bf_attr_desc_factory_base
from bes.files.attr.bf_attr_desc_registry import bf_attr_desc_registry
from bes.files.attr.bf_attr_type_desc_base import bf_attr_type_desc_base

from _bes_unit_test_common.files.attr.fruits_factory import fruits_factory

class test_bf_attr_desc_registry(unit_test):

  @classmethod
  def setUpClass(clazz):
    bf_attr_desc_registry.register_factory(fruits_factory)

  def test_register_attr_value_desc_factory(self):
    self.assertEqual( True, bf_attr_desc_registry.has_value('acme/fruit/kiwi/1.0') )
    self.assertEqual( False, bf_attr_desc_registry.has_value('acme/fruit/kiwi/2.0') )
    self.assertEqual( False, bf_attr_desc_registry.has_value('acme/fruit/cherry/1.0') )
    self.assertEqual( True, bf_attr_desc_registry.has_value('acme/fruit/cherry/2.0') )

  class _kiwi1_type_desc(bf_attr_type_desc_base):
    @classmethod
    def name(clazz):
      return '_kiwi1_type_desc'
      
    @classmethod
    def encoder(clazz):
      return lambda v: 1
    
    @classmethod
    def decoder(clazz):
      return lambda v: b'1'
    
    @classmethod
    def checker(clazz):
      return lambda v: v
    
    @classmethod
    def description(clazz):
      return '_kiwi1_type_desc'

  class _kiwi2_type_desc(bf_attr_type_desc_base):
    @classmethod
    def name(clazz):
      return '_kiwi2_type_desc'
      
    @classmethod
    def encoder(clazz):
      return lambda v: 2
    
    @classmethod
    def decoder(clazz):
      return lambda v: b'2'
    
    @classmethod
    def checker(clazz):
      return lambda v: v
    
    @classmethod
    def description(clazz):
      return '_kiwi2_type_desc'
    
  def test_register_factory_duplicate(self):
    
    class _kiwi1_factory(bf_attr_desc_factory_base):
      @classmethod
      #@abstractmethod
      def descriptions(clazz):
        return [
          ( 'kiwi', 'Kiwi', self._kiwi1_type_desc, None ),
        ]
    with self.assertRaises(bf_attr_error) as ctx:
      class _kiwi2_factory(bf_attr_desc_factory_base):
        @classmethod
        #@abstractmethod
        def descriptions(clazz):
          return [
            ( 'kiwi', 'Kiwi', self._kiwi2_type_desc, None ),
          ]
    bf_attr_desc_registry.unregister_factory(_kiwi1_factory)
    
  def test_register_factory_duplicate_same_descriptions(self):
    class _kiwi_factory(bf_attr_desc_factory_base):
      @classmethod
      #@abstractmethod
      def descriptions(clazz):
        return [
          ( 'kiwi', 'Kiwi', self._kiwi1_type_desc, None ),
        ]
    bf_attr_desc_registry.register_factory(_kiwi_factory)
    bf_attr_desc_registry.register_factory(_kiwi_factory)
    bf_attr_desc_registry.unregister_factory(_kiwi_factory)
    
if __name__ == '__main__':
  unit_test.main()

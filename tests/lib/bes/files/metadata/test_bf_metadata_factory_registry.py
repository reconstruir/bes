#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.files.metadata.bf_metadata_factory_registry import bf_metadata_factory_registry

from _bes_unit_test_common.files.metadata.example_metadata_fruits_factory import example_metadata_fruits_factory

class test_bf_metadata_factory_registry(unit_test):

#  @classmethod
#  def setUpClass(clazz):
#    bf_metadata_factory_registry.unregister_factory(_test_fruits_factory)
#    bf_metadata_factory_registry.register_factory(_test_fruits_factory)

#  @classmethod
#  def tearDownClass(clazz):
#    bf_metadata_factory_registry.unregister_factory(_test_fruits_factory)
  
  def test_register_attr_factory(self):
    self.assertEqual( True, bf_metadata_factory_registry.has_description('acme/fruit/kiwi/1.0') )
    self.assertEqual( False, bf_metadata_factory_registry.has_description('acme/fruit/kiwi/2.0') )
    self.assertEqual( False, bf_metadata_factory_registry.has_description('acme/fruit/cherry/1.0') )
    self.assertEqual( True, bf_metadata_factory_registry.has_description('acme/fruit/cherry/2.0') )
                                                                    
if __name__ == '__main__':
  unit_test.main()

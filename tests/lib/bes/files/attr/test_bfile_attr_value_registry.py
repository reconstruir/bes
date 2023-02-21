#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test

from bes.files.attr.bfile_attr_value_registry import bfile_attr_value_registry

from _bes_unit_test_common.files.attr.fruits_factory import fruits_factory as _test_fruits_factory

class test_bfile_attr_value_registry(unit_test):

  @classmethod
  def setUpClass(clazz):
    bfile_attr_value_registry.unregister_factory(_test_fruits_factory)
    bfile_attr_value_registry.register_factory(_test_fruits_factory)

  @classmethod
  def tearDownClass(clazz):
    bfile_attr_value_registry.unregister_factory(_test_fruits_factory)
  
  def test_register_attr_value_handler_factory(self):
    self.assertEqual( True, bfile_attr_value_registry.has_value('acme/fruit/kiwi/1.0') )
    self.assertEqual( False, bfile_attr_value_registry.has_value('acme/fruit/kiwi/2.0') )
    self.assertEqual( False, bfile_attr_value_registry.has_value('acme/fruit/cherry/1.0') )
    self.assertEqual( True, bfile_attr_value_registry.has_value('acme/fruit/cherry/2.0') )
                                                                    
if __name__ == '__main__':
  unit_test.main()

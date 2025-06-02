#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.files.metadata.bf_metadata_factory_registry import bf_metadata_factory_registry

from _bes_unit_test_common.files.metadata.example_metadata_fruits_factory import example_metadata_fruits_factory

class test_bf_metadata_factory_registry(unit_test):

  def test_register_attr_factory(self):
    self.assertEqual( True, bf_metadata_factory_registry.has_description('acme__fruit__kiwi__1.0') )
    self.assertEqual( False, bf_metadata_factory_registry.has_description('acme__fruit__kiwi__2.0') )
    self.assertEqual( False, bf_metadata_factory_registry.has_description('acme__fruit__cherry__1.0') )
    self.assertEqual( True, bf_metadata_factory_registry.has_description('acme__fruit__cherry__2.0') )
                                                                    
if __name__ == '__main__':
  unit_test.main()

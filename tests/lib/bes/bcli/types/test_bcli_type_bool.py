#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.bcli.types.bcli_type_bool import bcli_type_bool

class test_bcli_type_bool(unit_test):

  def test_parse(self):
    self.assertEqual( True, bcli_type_bool().parse('true') )
    self.assertEqual( False, bcli_type_bool().parse('false') )

  def test_check(self):
    self.assertEqual( True, bcli_type_bool().check(True) )

  def test_type_function(self):
    self.assertEqual( bool, bcli_type_bool().type_function()() )

  def test_type(self):
    self.assertEqual( bool, bcli_type_bool().type )
    
if __name__ == '__main__':
  unit_test.main()

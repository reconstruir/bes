#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.bcli.types.bcli_type_float import bcli_type_float

class test_bcli_type_float(unit_test):

  def test_parse(self):
    self.assertEqual( 4.2, bcli_type_float().parse('4.2') )

  def test_check(self):
    self.assertEqual( 4.2, bcli_type_float().check(4.2) )

  def test_type_function(self):
    self.assertEqual( float, bcli_type_float().type_function()() )

  def test_type(self):
    self.assertEqual( float, bcli_type_float().type )
    
if __name__ == '__main__':
  unit_test.main()

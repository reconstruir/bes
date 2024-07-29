#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.bcli.types.bcli_type_int import bcli_type_int

class test_bcli_type_int(unit_test):

  def test_parse(self):
    self.assertEqual( 42, bcli_type_int().parse('42') )

  def test_check(self):
    self.assertEqual( 42, bcli_type_int().check(42) )

  def test_type_function(self):
    self.assertEqual( int, bcli_type_int().type_function() )

  def test_type(self):
    self.assertEqual( int, bcli_type_int().type )
    
if __name__ == '__main__':
  unit_test.main()

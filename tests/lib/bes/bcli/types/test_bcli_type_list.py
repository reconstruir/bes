#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.bcli.types.bcli_type_list import bcli_type_list

class test_bcli_type_list(unit_test):

  def test_parse(self):
    self.assertEqual( [ 42, 43 ], bcli_type_list().parse('[ 42, 43 ]') )

  def test_check(self):
    self.assertEqual( [ 42, 43 ], bcli_type_list().check([ 42, 43 ]) )

  def test_type_function(self):
    self.assertEqual( list, bcli_type_list().type_function() )

  def test_type(self):
    self.assertEqual( list, bcli_type_list().type )
    
if __name__ == '__main__':
  unit_test.main()

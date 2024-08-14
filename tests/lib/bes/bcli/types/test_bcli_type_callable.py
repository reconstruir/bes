#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.bcli.types.bcli_type_callable import bcli_type_callable

class test_bcli_type_callable(unit_test):

  def xtest_parse(self):
    self.assertEqual( 42, bcli_type_callable().parse('42') )

  def test_check(self):
    def f():
      pass
    self.assertEqual( f, bcli_type_callable().check(f) )

  def test_type_function(self):
    self.assertEqual( callable, bcli_type_callable().type_function() )

  def test_type(self):
    self.assertEqual( callable, bcli_type_callable().type )
    
if __name__ == '__main__':
  unit_test.main()

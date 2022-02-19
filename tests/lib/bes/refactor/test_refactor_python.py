#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.refactor.refactor_python import refactor_python
from bes.testing.unit_test import unit_test

class test_refactor_ast(unit_test):

  def test_function_definition(self):
    self.assert_string_equal_fuzzy(r'''
def foo(self, x)
''', refactor_python.function_definition(r'''
def foo(self, x):
  if x == 5:
    return 50
  elif x == ( 0, 1 ):
    return 51
  return None
''') )

  def test_function_definition_with_colon_in_definition(self):
    self.assert_string_equal_fuzzy(r'''
def foo(self, x = global[0:5])
''', refactor_python.function_definition(r'''
def foo(self, x = global[0:5]):
  if x == 5:
    return 50
  elif x == ( 0, 1 ):
    return 51
  return None
''') )

  def test_function_definition_multi_line(self):
    self.assert_string_equal_fuzzy(r'''
def foo(self, x,
        y)
''', refactor_python.function_definition(r'''
def foo(self, x,
        y):
  if x == 5:
    return 50
  elif x == ( 0, 1 ):
    return 51
  return None
''') )
    
if __name__ == '__main__':
  unit_test.main()

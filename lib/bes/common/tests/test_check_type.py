#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-
from bes.testing.unit_test import unit_test
from bes.common import check_type as C

class test_check_type(unit_test):

  def test_check_bool(self):
    C.check_bool(True, 'n')

    with self.assertRaises(TypeError) as context:
      C.check_bool(6, 'n')

  def test_string(self):
    C.check_string('x', 'n')

    with self.assertRaises(TypeError) as context:
      C.check_string(6, 'n')

  def test_string_list(self):
    C.check_string_list(['x'], 'n')

    with self.assertRaises(TypeError) as context:
      C.check_string_list(6, 'n')
      C.check_string(6, 'n')

  def test_add_check(self):
    class foo(object): pass
    C.add_check(foo, 'foo')
    C.check_foo(foo(), 'n')
    
    with self.assertRaises(TypeError) as context:
      C.check_foo(6, 'n')

  def test_add_check_duplicate(self):
    class bar(object): pass
    C.add_check(bar, 'bar')
    with self.assertRaises(RuntimeError) as context:
      C.add_check(bar, 'bar')

if __name__ == '__main__':
  unit_test.main()

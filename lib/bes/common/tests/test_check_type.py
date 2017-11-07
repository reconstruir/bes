#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
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

if __name__ == '__main__':
  unit_test.main()

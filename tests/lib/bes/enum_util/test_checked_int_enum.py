#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.enum_util.checked_int_enum import checked_int_enum

class test_checked_int_enum(unit_test):

  def test_foo(self):
    self.assertTrue( True )
    
if __name__ == '__main__':
  unit_test.main()

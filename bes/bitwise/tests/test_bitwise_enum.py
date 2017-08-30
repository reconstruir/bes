#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
from bes.test import unit_test_helper
from bes.bitwise import bitwise_enum as E

class test_bitwise_enum(unit_test_helper):

  class fruit(E):
    SIZE = 1

    PEAR = 1
    APPLE = 2
    KIWI = 3

    DEFAULT = PEAR
  
  def test_default_value(self):
    F = self.fruit
    self.assertEqual( F.PEAR, F().value )
    
  def test_init_value(self):
    F = self.fruit
    self.assertEqual( F.APPLE, F(F.APPLE).value )
    self.assertEqual( F.KIWI, F(F.KIWI).value )
    self.assertEqual( F.KIWI, F(F.KIWI).value )
    
  def test_set_value(self):
    F = self.fruit
    f = F()
    f.value = F.APPLE
    self.assertEqual( F.APPLE, f.value )
    f.value = F.KIWI
    self.assertEqual( F.KIWI, f.value )
    
if __name__ == "__main__":
  unit_test_helper.main()

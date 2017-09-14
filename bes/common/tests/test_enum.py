#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
from bes.testing.unit_test import unit_test
from bes.common import enum

'''
class fruit(enum):
  PEAR = 1
  APPLE = 2
  KIWI = 3
  KIWI_CLONE = KIWI
  DEFAULT = PEAR
'''

class test_enum(unit_test):

  def test_name_is_valid(self):
    e = enum()
    e.add_value('PEAR', 1)
    e.add_value('APPLE', 2)
    e.add_value('KIWI', 3)
    e.add_value('ALSO_KIWI', 3)
    self.assertTrue( e.name_is_valid('PEAR') )
    self.assertTrue( e.name_is_valid('APPLE') )
    self.assertTrue( e.name_is_valid('KIWI') )
    self.assertTrue( e.name_is_valid('ALSO_KIWI') )
    self.assertFalse( e.name_is_valid('MELON') )

  def test_name_is_valid_lower_case(self):
    e = enum()
    e.add_value('PEAR', 1)
    e.add_value('APPLE', 2)
    e.add_value('KIWI', 3)
    e.add_value('ALSO_KIWI', 3)
    self.assertTrue( e.name_is_valid('pear') )
    self.assertTrue( e.name_is_valid('apple') )
    self.assertTrue( e.name_is_valid('kiwi') )
    self.assertTrue( e.name_is_valid('also_kiwi') )
    self.assertFalse( e.name_is_valid('melon') )

  def test_value_is_valid(self):
    e = enum()
    e.add_value('PEAR', 1)
    e.add_value('APPLE', 2)
    e.add_value('KIWI', 3)
    self.assertTrue( e.value_is_valid(1) )
    self.assertTrue( e.value_is_valid(2) )
    self.assertTrue( e.value_is_valid(3) )
    self.assertFalse( e.value_is_valid(4) )
    
  def test_default_value(self):
    e = enum()
    e.add_value('PEAR', 1)
    e.add_value('APPLE', 2)
    e.default_value = 2
    self.assertEqual( 2, e.default_value )
    
  def test_default_value_invalid(self):
    e = enum()
    e.add_value('PEAR', 1)
    e.add_value('APPLE', 2)
    with self.assertRaises(ValueError) as context:
      e.default_value = 666

  def test_parse_name(self):
    e = enum()
    e.add_value('PEAR', 1)
    e.add_value('APPLE', 2)
    e.add_value('KIWI', 3)
    e.add_value('ALSO_KIWI', 3)
    self.assertEqual( 1, e.parse_name('PEAR') )
    self.assertEqual( 2, e.parse_name('APPLE') )
    self.assertEqual( 3, e.parse_name('KIWI') )
    self.assertEqual( 3, e.parse_name('ALSO_KIWI') )

  def test_multiple_names(self):
    e = enum()
    e.add_value('PEAR', 1)
    e.add_value('APPLE', 2)
    e.add_value('KIWI', 3)
    e.add_value('P', 1)
    e.add_value('A', 2)
    e.add_value('K', 3)
    self.assertTrue( e.name_is_valid('PEAR') )
    self.assertTrue( e.name_is_valid('APPLE') )
    self.assertTrue( e.name_is_valid('KIWI') )
    self.assertTrue( e.name_is_valid('P') )
    self.assertTrue( e.name_is_valid('A') )
    self.assertTrue( e.name_is_valid('K') )

    
if __name__ == '__main__':
  unit_test.main()

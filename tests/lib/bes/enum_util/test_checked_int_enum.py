#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.enum_util.checked_int_enum import checked_int_enum

class test_checked_int_enum(unit_test):

  class _fruit(checked_int_enum):
    LEMON = 1
    PEACH = 2
    ORANGE = 3
    
  def test_value_is_valid(self):
    self.assertTrue( self._fruit.value_is_valid(1) )
    self.assertTrue( self._fruit.value_is_valid(2) )
    self.assertFalse( self._fruit.value_is_valid(4) )

  def test_name_is_valid(self):
    self.assertTrue( self._fruit.name_is_valid('LEMON') )
    self.assertTrue( self._fruit.name_is_valid('PEACH') )
    self.assertFalse( self._fruit.name_is_valid('COCONUT') )

  def test_name_to_value_dict(self):
    self.assertEqual( {
      'LEMON': 1,
      'ORANGE': 3,
      'PEACH': 2,
    }, self._fruit.name_to_value_dict )

  def test_name_to_item_dict(self):
    self.assertEqual( {
      'LEMON': self._fruit.LEMON,
      'ORANGE': self._fruit.ORANGE,
      'PEACH': self._fruit.PEACH,
    }, self._fruit.name_to_value_dict )
    
  def test_value_to_name_dict(self):
    self.assertEqual( {
      1: { 'LEMON' },
      2: { 'PEACH' },
      3: { 'ORANGE' },
    }, self._fruit.value_to_name_dict )

  def test_parse(self):
    self.assertEqual( self._fruit.LEMON, self._fruit.parse('LEMON') )
    self.assertEqual( self._fruit.LEMON, self._fruit.parse(1) )
    self.assertEqual( self._fruit.LEMON, self._fruit.parse(self._fruit.LEMON) )
    
if __name__ == '__main__':
  unit_test.main()

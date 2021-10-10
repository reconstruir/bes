#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.enum_util.checked_enum import checked_enum
from bes.system.check import check

class test_checked_enum(unit_test):

  class _fruit(checked_enum):
    LEMON = 'lemon'
    PEACH = 'peach'
    ORANGE = 'orange'
    
  def test_value_is_valid(self):
    self.assertTrue( self._fruit.value_is_valid('lemon') )
    self.assertTrue( self._fruit.value_is_valid('peach') )
    self.assertFalse( self._fruit.value_is_valid('fig') )

  def test_name_is_valid(self):
    self.assertTrue( self._fruit.name_is_valid('LEMON') )
    self.assertTrue( self._fruit.name_is_valid('PEACH') )
    self.assertFalse( self._fruit.name_is_valid('COCONUT') )

  def test_name_to_value_dict(self):
    self.assertEqual( {
      'LEMON': 'lemon',
      'ORANGE': 'orange',
      'PEACH': 'peach',
    }, self._fruit.name_to_value_dict )

  def test_name_to_item_dict(self):
    self.assertEqual( {
      'LEMON': self._fruit.LEMON,
      'ORANGE': self._fruit.ORANGE,
      'PEACH': self._fruit.PEACH,
    }, self._fruit.name_to_item_dict )

  def test_value_to_name_dict(self):
    self.assertEqual( {
      'lemon': { 'LEMON' },
      'peach': { 'PEACH' },
      'orange': { 'ORANGE' },
    }, self._fruit.value_to_name_dict )

  def test_parse(self):
    self.assertEqual( self._fruit.LEMON, self._fruit.parse('lemon') )
    self.assertEqual( self._fruit.LEMON, self._fruit.parse(self._fruit.LEMON) )
    self.assertEqual( self._fruit.LEMON, self._fruit.parse('LEMON') )

  def test_parse_invalid_type(self):
    class _bread(object):
      pass
    with self.assertRaises(ValueError) as ctx:
      self._fruit.parse(_bread())
    
  def test_check(self):
    class _dessert(checked_enum):
      FRUIT = 'fruit'
      CHEESECAKE = 'cheesecake'
      CHEESE = 'cheese'
    check.register_class(_dessert)
    check.check__dessert(_dessert.CHEESE)

    with self.assertRaises(TypeError) as ctx:
      check.check__dessert('fruit')
      
    with self.assertRaises(TypeError) as ctx:
      check.check__dessert('CHEESE')

  def test_check_with_cast_func(self):
    class _spread(checked_enum):
      CREAM_CHEESE = 'cream_cheese'
      JAM = 'JAM'
      BUTTER = 'BUTTER'
    check.register_class(_spread, cast_func = _spread.parse)
    self.assertEqual( _spread.BUTTER, check.check__spread(_spread.BUTTER) )
    self.assertEqual( _spread.CREAM_CHEESE, check.check__spread('cream_cheese') )
    self.assertEqual( _spread.JAM, check.check__spread('JAM') )
    
if __name__ == '__main__':
  unit_test.main()

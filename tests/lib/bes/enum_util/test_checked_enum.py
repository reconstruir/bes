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

  def test_parse_name_str_value(self):
    class _E(checked_enum):
      A = 'a'
      C = 'c'
    self.assertEqual( _E.A, _E.parse_name('a') )
    self.assertEqual( _E.A, _E.parse_name('A') )
    self.assertEqual( _E.C, _E.parse_name('c') )
    self.assertEqual( _E.C, _E.parse_name('c') )
    self.assertEqual( None, _E.parse_name('d') )

  def test_parse_name_int_value(self):
    class _E(checked_enum):
      A = 1
      C = 2
    self.assertEqual( _E.A, _E.parse_name('a') )
    self.assertEqual( _E.A, _E.parse_name('A') )
    self.assertEqual( _E.C, _E.parse_name('c') )
    self.assertEqual( _E.C, _E.parse_name('c') )
    self.assertEqual( None, _E.parse_name('d') )

  def test_parse_name_str_value_with_name_conflict(self):
    class _E(checked_enum):
      A = 'A'
      a = 'a'
    with self.assertRaises(ValueError) as _:
      _E.parse_name('a')
    
  def test_value_is_valid(self):
    self.assertTrue( self._fruit.value_is_valid('lemon') )
    self.assertTrue( self._fruit.value_is_valid('LEMON') )
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
      'lemon': self._fruit.LEMON,
      'orange': self._fruit.ORANGE,
      'peach': self._fruit.PEACH,
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

  def test_parse_list(self):
    self.assertEqual( [
      self._fruit.PEACH,
      self._fruit.LEMON,
      self._fruit.ORANGE,
      ], self._fruit.parse_list('peach lemon orange') )
    
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

  class _spread(checked_enum):
    CREAM_CHEESE = 'CREAM_CHEESE'
    JAM = 'JAM'
    BUTTER = 'BUTTER'
    
  def test_check_with_cast_func(self):
    check.register_class(self._spread, cast_func = self._spread.parse)
    self.assertEqual( self._spread.BUTTER, check.check__spread(self._spread.BUTTER) )
    self.assertEqual( self._spread.CREAM_CHEESE, check.check__spread('CREAM_CHEESE') )
    self.assertEqual( self._spread.JAM, check.check__spread('JAM') )
    check.unregister_class(self._spread)

  def test___gt__(self):
    self.assertTrue( self._spread.JAM > self._spread.BUTTER )
    self.assertTrue( self._spread.JAM > 'BUTTER' )

  def test___eq__(self):
    self.assertTrue( self._spread.JAM == 'JAM' )
    self.assertTrue( self._spread.JAM == self._spread.JAM )
    
if __name__ == '__main__':
  unit_test.main()

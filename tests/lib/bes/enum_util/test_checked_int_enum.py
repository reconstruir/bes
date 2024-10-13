#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.enum_util.checked_int_enum import checked_int_enum
from bes.system.check import check

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
      'lemon': self._fruit.LEMON,
      'orange': self._fruit.ORANGE,
      'peach': self._fruit.PEACH,
    }, self._fruit.name_to_item_dict )

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

  def test_parse_invalid_type(self):
    class _bread(object):
      pass
    with self.assertRaises(ValueError) as ctx:
      self._fruit.parse(_bread())
    
  def test_check(self):
    class _cheese(checked_int_enum):
      BRIE = 1
      CHEDDAR = 2
      GOUDA = 3
    check.register_class(_cheese)
    check.check__cheese(_cheese.GOUDA)

    with self.assertRaises(TypeError) as ctx:
      check.check__cheese(1)
      
    with self.assertRaises(TypeError) as ctx:
      check.check__cheese('GOUDA')

  class _wine(checked_int_enum):
    SANCERRE = 1
    CHABLIS = 2
    OPORTO = 3
    
  def test_check_with_cast_func(self):
    check.register_class(self._wine, cast_func = self._wine.parse)
    self.assertEqual( self._wine.OPORTO, check.check__wine(self._wine.OPORTO) )
    self.assertEqual( self._wine.SANCERRE, check.check__wine(1) )
    self.assertEqual( self._wine.CHABLIS, check.check__wine('CHABLIS') )
    check.unregister_class(self._wine)

  def test___gt__(self):
    self.assertTrue( self._wine.OPORTO > self._wine.CHABLIS )
    self.assertTrue( self._wine.OPORTO > 'CHABLIS' )
    self.assertTrue( self._wine.OPORTO > 2 )

  def test___eq__(self):
    self.assertTrue( self._wine.OPORTO == self._wine.OPORTO )
    self.assertFalse( self._wine.OPORTO == self._wine.CHABLIS )
    self.assertTrue( self._wine.OPORTO == 'OPORTO' )
    self.assertTrue( self._wine.OPORTO == 3 )
    
if __name__ == '__main__':
  unit_test.main()

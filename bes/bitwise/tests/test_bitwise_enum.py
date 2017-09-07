#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
from bes.testing.unit_test import unit_test
from bes.bitwise import bitwise_enum

class fruit(bitwise_enum):
  SIZE = 1

  PEAR = 1
  APPLE = 2
  KIWI = 3
  KIWI_CLONE = KIWI
    
  DEFAULT = PEAR
  
class test_bitwise_enum(unit_test):

  def test_default_value(self):
    self.assertEqual( fruit.PEAR, fruit().value )
    
  def test_init_value(self):
    self.assertEqual( fruit.APPLE, fruit(fruit.APPLE).value )
    self.assertEqual( fruit.KIWI, fruit(fruit.KIWI).value )
    self.assertEqual( fruit.KIWI, fruit(fruit.KIWI).value )
    
  def test_set_value(self):
    f = fruit()
    f.value = fruit.APPLE
    self.assertEqual( fruit.APPLE, f.value )
    f.value = fruit.KIWI
    self.assertEqual( fruit.KIWI, f.value )
    
    f.value = 3
    self.assertEqual( fruit.KIWI, f.value )

  def test_set_value_invalid(self):
    with self.assertRaises(ValueError) as context:
      fruit().value = 666
    
  def test___str__(self):
    self.assertEqual( 'PEAR', str(fruit()) )
    self.assertEqual( 'KIWI', str(fruit(fruit.KIWI)) )
    self.assertEqual( 'KIWI', str(fruit(fruit.KIWI_CLONE)) )

  def test_set_name(self):
    f = fruit()
    f.name = 'PEAR'
    self.assertEqual( f.value, fruit.PEAR )
    
  def test_set_name_invalid(self):
    with self.assertRaises(ValueError) as context:
      fruit().name = 'NOTHERE'
    
  def test_assign(self):
    f = fruit()
    f.assign('KIWI')
    self.assertEqual( 'KIWI', f.name )
    f.assign(2)
    self.assertEqual( 'APPLE', f.name )
    f.assign(fruit('APPLE'))
    self.assertEqual( 'APPLE', f.name )

    with self.assertRaises(ValueError) as context:
      f.assign('NOTHERE')

    with self.assertRaises(ValueError) as context:
      f.assign(666)
    
if __name__ == "__main__":
  unit_test.main()

#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.enum.enum import enum
from bes.common.check import check

class example_fruit_enum(enum):
  SIZE = 1

  PEAR = 1
  APPLE = 2
  KIWI = 3
  KIWI_CLONE = KIWI
    
  DEFAULT = PEAR
  
class test_enum(unit_test):

  def test_default_value(self):
    self.assertEqual( example_fruit_enum.PEAR, example_fruit_enum().value )
    self.assertEqual( example_fruit_enum.PEAR, example_fruit_enum('DEFAULT').value )
    
  def test__init___value(self):
    self.assertEqual( example_fruit_enum.APPLE, example_fruit_enum(example_fruit_enum.APPLE).value )
    self.assertEqual( example_fruit_enum.KIWI, example_fruit_enum(example_fruit_enum.KIWI).value )
    self.assertEqual( example_fruit_enum.KIWI, example_fruit_enum(example_fruit_enum.KIWI).value )

  def test___init___from_string(self):
    self.assertEqual( example_fruit_enum.APPLE, example_fruit_enum('APPLE') )
    self.assertEqual( example_fruit_enum.KIWI, example_fruit_enum('KIWI') )
    self.assertEqual( example_fruit_enum.KIWI, example_fruit_enum('KIWI_CLONE') )
    
  def test___init___invalid_value(self):
    with self.assertRaises(ValueError) as context:
      example_fruit_enum(666)
    
  def test___init___invalid_name(self):
    with self.assertRaises(ValueError) as context:
      example_fruit_enum('666')
    
  def test_set_value(self):
    f = example_fruit_enum()
    f.value = example_fruit_enum.APPLE
    self.assertEqual( example_fruit_enum.APPLE, f.value )
    f.value = example_fruit_enum.KIWI
    self.assertEqual( example_fruit_enum.KIWI, f.value )
    
    f.value = 3
    self.assertEqual( example_fruit_enum.KIWI, f.value )

  def test_set_value_invalid(self):
    with self.assertRaises(ValueError) as context:
      example_fruit_enum().value = 666
    
  def test___str__(self):
    self.assertEqual( 'PEAR', str(example_fruit_enum()) )
    self.assertEqual( 'KIWI', str(example_fruit_enum(example_fruit_enum.KIWI)) )
    self.assertEqual( 'KIWI', str(example_fruit_enum(example_fruit_enum.KIWI_CLONE)) )

  def test_set_name(self):
    f = example_fruit_enum()
    f.name = 'PEAR'
    self.assertEqual( f.value, example_fruit_enum.PEAR )
    
  def test_set_name_invalid(self):
    with self.assertRaises(ValueError) as context:
      example_fruit_enum().name = 'NOTHERE'
    
  def test_assign(self):
    f = example_fruit_enum()
    f.assign('KIWI')
    self.assertEqual( 'KIWI', f.name )
    f.assign(2)
    self.assertEqual( 'APPLE', f.name )
    f.assign(example_fruit_enum('APPLE'))
    self.assertEqual( 'APPLE', f.name )

    with self.assertRaises(ValueError) as context:
      f.assign('NOTHERE')

    with self.assertRaises(ValueError) as context:
      f.assign(666)
    
  def test_parse(self):
    self.assertEqual( example_fruit_enum('KIWI'), example_fruit_enum.parse('KIWI') )

  def test_name_is_valid(self):
    self.assertTrue( example_fruit_enum.name_is_valid('PEAR') )
    self.assertFalse( example_fruit_enum.name_is_valid('NOTTHERE') )
    
  def test_value_is_valid(self):
    self.assertTrue( example_fruit_enum.value_is_valid(1) )
    self.assertFalse( example_fruit_enum.value_is_valid(666) )
    
  def test_is_valid(self):
    self.assertTrue( example_fruit_enum.is_valid(1) )
    self.assertFalse( example_fruit_enum.is_valid(666) )
    self.assertTrue( example_fruit_enum.is_valid('PEAR') )
    self.assertFalse( example_fruit_enum.is_valid('NOTTHERE') )
    
  def test_size(self):
    class cheese(enum):
      SIZE = 4
      GOUDA = 110
      BLUE = 120
      ROMANO = 130
    self.assertEqual( 4, cheese.SIZE )
    
  def test_default_size(self):
    class foo(enum):
      A = 1
      B = 2
    self.assertEqual( 1, foo.SIZE )
    
  def test_check(self):
    class bar1(enum):
      A = 1
      B = 2
    check.check_bar1(bar1(2))

  def test_check_int_cast(self):
    class bar2(enum):
      A = 1
      B = 2
    check.check_bar2(2)

  def test_check_invalid_value(self):
    class bar3(enum):
      A = 1
      B = 2
    with self.assertRaises(ValueError) as _:
      check.check_bar3(666)
    
  def test_check_string_cast(self):
    class bar4(enum):
      A = 1
      B = 2
    check.check_bar4('A')

if __name__ == '__main__':
  unit_test.main()

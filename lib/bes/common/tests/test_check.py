#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-
from bes.testing.unit_test import unit_test
from bes.common import check as C

class test_check(unit_test):

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

  def test_register_class(self):
    class foo(object): pass
    C.register_class(foo, 'foo')
    C.check_foo(foo(), 'n')
    
    with self.assertRaises(TypeError) as context:
      C.check_foo(6, 'n')

  def test_register_class_duplicate(self):
    class bar(object): pass
    C.register_class(bar, 'bar')
    with self.assertRaises(RuntimeError) as context:
      C.register_class(bar, 'bar')

  def test_is(self):
    class baz(object): pass
    C.register_class(baz, 'baz')
    self.assertTrue( C.is_baz(baz()) )
    self.assertFalse( C.is_baz(int(6)) )

  def test_is_seq(self):
    class kiwi(object): pass
    C.register_class(kiwi, 'kiwi')
    self.assertTrue( C.is_kiwi_seq([ kiwi(), kiwi() ]) )
    self.assertFalse( C.is_kiwi_seq([ kiwi(), int(6) ]) )

  def test_is_seq_not_registered(self):
    class apple(object): pass
    C.register_class(apple, 'apple', include_seq = False)
    with self.assertRaises(AttributeError) as context:
      self.assertTrue( C.is_apple_seq([ apple(), apple() ]) )

  def test_is_seq_without_reigstration(self):
    self.assertTrue( C.is_seq([ 1, 2, 3, 4 ], int) )
    self.assertFalse( C.is_seq([ '1', 2, 3, 4 ], int ) )
    self.assertTrue( C.is_seq([ '1', 2, 3, 4 ], ( int, str )) )
    self.assertFalse( C.is_seq(False, bool) )
      
  def test_check_seq(self):
    class orange(object): pass
    C.register_class(orange, 'orange')
    C.check_orange_seq([ orange(), orange() ], 'n')

  def test_check_seq(self):
    class potato(object): pass
    C.register_class(potato, 'potato', include_seq = False)
    with self.assertRaises(AttributeError) as context:
      C.check_potato_seq([ potato(), potato() ], 'n')
      
if __name__ == '__main__':
  unit_test.main()

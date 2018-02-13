#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.common import check as C
from bes.system import compat

class test_check(unit_test):

  def test_check_bool(self):
    C.check_bool(True)

    with self.assertRaises(TypeError) as context:
      C.check_bool(6)

  def test_string(self):
    C.check_string('x')

    with self.assertRaises(TypeError) as context:
      C.check_string(6)

  def test_string_seq(self):
    C.check_string_seq(['x'])

    with self.assertRaises(TypeError) as context:
      C.check_string_seq(6)
      C.check_string(6)

  def test_register_class(self):
    class foo(object): pass
    C.register_class(foo, 'foo')
    C.check_foo(foo())
    
    with self.assertRaises(TypeError) as context:
      C.check_foo(6)

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
    C.check_orange_seq([ orange(), orange() ])

  def test_check_seq(self):
    class potato(object): pass
    C.register_class(potato, 'potato', include_seq = False)
    with self.assertRaises(AttributeError) as context:
      C.check_potato_seq([ potato(), potato() ])
      
  def test_check_dict(self):
    C.check_dict({ 'a': 5 })
    with self.assertRaises(TypeError) as context:
      C.check_dict(True)
      
  def test_check_dict_and_key(self):
    C.check_dict({ 'a': 5, 'b': 6 }, key_type = compat.STRING_TYPES)
    with self.assertRaises(TypeError) as context:
      C.check_dict({ 'a': 5, 6: 'b' }, key_type = compat.STRING_TYPES)
      
  def test_check_dict_and_value(self):
    C.check_dict({ 'a': 5, 'b': 6 }, value_type = compat.INTEGER_TYPES)
    with self.assertRaises(TypeError) as context:
      C.check_dict({ 'a': 5, 6: 'b' }, value_type = compat.INTEGER_TYPES)

  def test_is_string_seq(self):
    self.assertFalse( C.is_string([ 'foo' ]) )
    self.assertTrue( C.is_string('foo') )
      
  def test_is_string_seq(self):
    self.assertTrue( C.is_string_seq([ 'foo' ]) )
    self.assertFalse( C.is_string_seq('foo') )
      
if __name__ == '__main__':
  unit_test.main()

#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.system.check import check
from bes.system.compat import compat

class test_check(unit_test):

  def test_check_bool(self):
    check.check_bool(True)

    with self.assertRaises(TypeError) as context:
      check.check_bool(6)

  def test_string(self):
    check.check_string('x')

  def test_string_int_error(self):
    with self.assertRaises(TypeError) as context:
      check.check_string(6)

  def test_string_seq_error(self):
    with self.assertRaises(TypeError) as context:
      check.check_string([ 'a '])

  def test_string_seq(self):
    check.check_string_seq(['x'])

  def test_string_seq_int_error(self):
    with self.assertRaises(TypeError) as context:
      check.check_string_seq(6)

  def test_string_seq_string_error(self):
    with self.assertRaises(TypeError) as context:
      check.check_string_seq('foo')
      
  def test_register_class(self):
    class _test_check_foo(object): pass
    check.register_class(_test_check_foo, '_test_check_foo')
    check.check__test_check_foo(_test_check_foo())
    
    with self.assertRaises(TypeError) as context:
      check.check__test_check_foo(6)

  def test_register_class_duplicate(self):
    class _test_check_bar(object): pass
    check.register_class(_test_check_bar, '_test_check_bar')
    with self.assertRaises(RuntimeError) as context:
      check.register_class(_test_check_bar, '_test_check_bar')

  def test_is(self):
    class _test_check_baz(object): pass
    check.register_class(_test_check_baz, '_test_check_baz')
    self.assertTrue( check.is__test_check_baz(_test_check_baz()) )
    self.assertFalse( check.is__test_check_baz(int(6)) )

  def test_is_seq(self):
    class _test_check_kiwi(object): pass
    check.register_class(_test_check_kiwi, '_test_check_kiwi')
    self.assertTrue( check.is__test_check_kiwi_seq([ _test_check_kiwi(), _test_check_kiwi() ]) )
    self.assertFalse( check.is__test_check_kiwi_seq([ _test_check_kiwi(), int(6) ]) )

  def test_is_seq_not_registered(self):
    class _test_check_apple(object): pass
    check.register_class(_test_check_apple, '_test_check_apple', include_seq = False)
    with self.assertRaises(AttributeError) as context:
      self.assertTrue( check.is__test_check_apple_seq([ _test_check_apple(), _test_check_apple() ]) )

  def test_is_seq_without_reigstration(self):
    self.assertTrue( check.is_seq([ 1, 2, 3, 4 ], int) )
    self.assertFalse( check.is_seq([ '1', 2, 3, 4 ], int ) )
    self.assertTrue( check.is_seq([ '1', 2, 3, 4 ], ( int, str )) )
    self.assertFalse( check.is_seq(False, bool) )
      
  def test_check_seq(self):
    class _test_check_orange(object): pass
    check.register_class(_test_check_orange, '_test_check_orange')
    check.check__test_check_orange_seq([ _test_check_orange(), _test_check_orange() ])

  def test_check_seq(self):
    class _test_check_potato(object): pass
    check.register_class(_test_check_potato, '_test_check_potato', include_seq = False)
    with self.assertRaises(AttributeError) as context:
      check.check__test_check_potato_seq([ _test_check_potato(), _test_check_potato() ])
      
  def test_check_dict(self):
    check.check_dict({ 'a': 5 })
    with self.assertRaises(TypeError) as context:
      check.check_dict(True)
      
  def test_check_dict_and_key(self):
    check.check_dict({ 'a': 5, 'b': 6 }, key_type = compat.STRING_TYPES)
    with self.assertRaises(TypeError) as context:
      check.check_dict({ 'a': 5, 6: 'b' }, key_type = compat.STRING_TYPES)
      
  def test_check_dict_and_value(self):
    check.check_dict({ 'a': 5, 'b': 6 }, value_type = compat.INTEGER_TYPES)
    with self.assertRaises(TypeError) as context:
      check.check_dict({ 'a': 5, 6: 'b' }, value_type = compat.INTEGER_TYPES)

  def test_is_string_seq(self):
    self.assertFalse( check.is_string([ 'foo' ]) )
    self.assertTrue( check.is_string('foo') )
      
  def test_is_string_seq(self):
    self.assertTrue( check.is_string_seq([ 'foo' ]) )
    self.assertFalse( check.is_string_seq('foo') )
      
  def test_string_allow_none(self):
    self.assertEqual( None, check.check_string(None, allow_none = True) )

  def test_custom_class_allow_none(self):
    class _test_check_wine(object): pass
    check.register_class(_test_check_wine, '_test_check_wine')
    check.check__test_check_wine(_test_check_wine())
    check.check__test_check_wine(None, allow_none = True)
    check.check__test_check_wine_seq([ _test_check_wine(), _test_check_wine() ])
    check.check__test_check_wine_seq(None, allow_none = True)
    
if __name__ == '__main__':
  unit_test.main()

#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.key_value.key_value_list import key_value_list as KVL
from bes.key_value.key_value import key_value as KV
from bes.system.compat import compat
from bes.compat.cmp import cmp

class test_key_value_list(unit_test):

  def test___init__with_tuples(self):
    l = KVL( [ ( 'foo', 'hi' ), ( 'bar', 666 ) ] )
    self.assertEqual( 2, len(l) )
    self.assertTrue( isinstance(l[0], KV) )
    self.assertEqual( KV('foo', 'hi'), l[0] )
    self.assertTrue( isinstance(l[1], KV) )
    self.assertEqual( KV('bar', 666), l[1] )
    
  def test_append(self):
    l = KVL()
    l.append(KV('foo', 'hi'))
    self.assertEqual( 1, len(l) )
    self.assertEqual( KV('foo', 'hi'), l[0] )
    
  def test_to_string(self):
    l = KVL()
    l.append(KV('foo', 'hi'))
    l.append(KV('bar', '666'))
    self.assertEqual( 'foo=hi;bar=666', l.to_string() )
    
  def test_contains_key(self):
    l = KVL()
    l.append(KV('foo', 'hi'))
    l.append(KV('bar', '666'))
    self.assertTrue( 'foo' in l )
    self.assertTrue( 'bar' in l )
    self.assertFalse( 'not' in l )
    
  def test_contains(self):
    l = KVL()
    l.append(KV('foo', 'hi'))
    l.append(KV('bar', '666'))
    self.assertTrue( KV('foo', 'hi') in l )
    self.assertTrue( KV('bar', '666') in l )
    self.assertFalse( KV('not', '') in l )
    self.assertFalse( KV('bar', '667') in l )
    
  def test_add(self):
    a = KVL()
    a.append(KV('foo', 'hi'))
    a.append(KV('bar', '666'))

    b = KVL()
    b.append(KV('apple', '6'))
    b.append(KV('kiwi', '7'))

    c = a + b
    self.assertEqual( 4, len(c) )
    it = iter(c)
    self.assertEqual( KV('foo', 'hi'), next(it) )
    self.assertEqual( KV('bar', '666'), next(it) )
    self.assertEqual( KV('apple', '6'), next(it) )
    self.assertEqual( KV('kiwi', '7'), next(it) )
    
  def test___eq__(self):
    a = KVL()
    a.append(KV('foo', 'hi'))
    a.append(KV('bar', '666'))

    b = KVL()
    b.append(KV('apple', '6'))
    b.append(KV('kiwi', '7'))

    self.assertFalse( a == b )
    
    c = KVL()
    c.append(KV('foo', 'hi'))
    c.append(KV('bar', '666'))

    self.assertTrue( a == c )

    self.assertEqual( a, [ KV('foo', 'hi'), KV('bar', '666') ] )
    self.assertEqual( [ KV('foo', 'hi'), KV('bar', '666') ], a )
    
  def test___cmp__(self):
    a = KVL()
    a.append(KV('foo', 'hi'))
    a.append(KV('bar', '666'))

    b = KVL()
    b.append(KV('apple', '6'))
    b.append(KV('kiwi', '7'))

    self.assertEqual( 1, cmp(a, b) )
    
    c = KVL()
    c.append(KV('foo', 'hi'))
    c.append(KV('bar', '666'))

    self.assertEqual( 0, cmp(a, c) )

  def test_remove(self):
    l = KVL()
    l.append(KV('foo', 'hi'))
    l.append(KV('bar', '666'))
    self.assertEqual( 2, len(l) )
    self.assertEqual( KV('foo', 'hi'), l[0] )
    self.assertEqual( KV('bar', '666'), l[1] )

    l.remove(KV('bar', '666'))

    self.assertEqual( 1, len(l) )
    self.assertEqual( KV('foo', 'hi'), l[0] )
    
  def test_remove_key(self):
    l = KVL()
    l.append(KV('foo', 'hi'))
    l.append(KV('bar', '666'))
    self.assertEqual( 2, len(l) )
    self.assertEqual( KV('foo', 'hi'), l[0] )
    self.assertEqual( KV('bar', '666'), l[1] )

    l.remove_key('bar')
    self.assertEqual( 1, len(l) )
    self.assertEqual( KV('foo', 'hi'), l[0] )
    
    l.remove_key('foo')
    self.assertEqual( 0, len(l) )

  def test_find_key_value(self):
    l = KVL()
    l.append(KV('foo', 'hi'))
    l.append(KV('bar', '666'))

    found = l.find_key_value(KV('foo', 'hi'))
    self.assertEqual( KV('foo', 'hi'), found )
    
    found = l.find_key_value(KV('foo', 'not'))
    self.assertEqual( None, found )
    
  def test_find_by_key(self):
    l = KVL()
    l.append(KV('foo', 'hi'))
    l.append(KV('bar', '666'))

    found = l.find_by_key('foo')
    self.assertEqual( KV('foo', 'hi'), found )
    
    found = l.find_by_key('not')
    self.assertEqual( None, found )
    
  def test_find_all_key(self):
    l = KVL()
    l.append(KV('foo', 'hi'))
    l.append(KV('bar', '666'))
    l.append(KV('foo', 'hi2'))

    found = l.find_all_key('foo')
    self.assertEqual( [ KV('foo', 'hi'), KV('foo', 'hi2') ], found )
    
  def test_is_homogeneous(self):
    l1 = KVL()
    l1.append(KV('foo', 666))
    l1.append(KV('bar', 667))
    l1.append(KV('foo', 668))
    self.assertEqual( True, l1.is_homogeneous(compat.STRING_TYPES, compat.INTEGER_TYPES) )

    l2 = KVL()
    l2.append(KV('foo', 666))
    l2.append(KV('bar', '667'))
    l2.append(KV('foo', 668))
    self.assertEqual( False, l2.is_homogeneous(compat.STRING_TYPES, compat.INTEGER_TYPES) )
    
  def test_from_dict(self):
    self.assertEqual( KVL([ KV('a', 5), KV('b', 6) ]), KVL.from_dict({ 'a': 5, 'b': 6 }) )

  def test_substitute_variables(self):
    l = KVL([( 'a', 'a is ${foo}' ), ( 'b', 'b is ${bar}' ) ])
    l.substitute_variables({ 'foo': 'apple', 'bar': 'kiwi' })
    self.assertEqual( KVL([ KV('a', 'a is apple'), KV('b', 'b is kiwi') ]), l )

if __name__ == "__main__":
  unit_test.main()

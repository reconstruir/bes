#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.text import string_list as SL
from bes.system import compat
from bes.compat import cmp

class test_string_list(unit_test):

  def test___init__with_tuples(self):
    l = SL( ( 'foo', 'hi' ) )
    self.assertEqual( 2, len(l) )
    
  def test_append(self):
    l = SL()
    l.append('foo')
    self.assertEqual( 1, len(l) )
    
  def test_to_string(self):
    l = SL()
    l.append('foo')
    l.append('bar')
    self.assertEqual( 'foo;bar', l.to_string() )
    
  def test_contains(self):
    l = SL()
    l.append('foo')
    l.append('bar')
    self.assertTrue( 'foo' in l )
    self.assertTrue( 'bar' in l )
    self.assertFalse( 'notthere' in l )
    
  def test_add(self):
    a = SL()
    a.append('foo')
    a.append('bar')

    b = SL()
    b.append('apple')
    b.append('kiwi')

    c = a + b
    self.assertEqual( 4, len(c) )
    it = iter(c)
    self.assertEqual( 'foo', next(it) )
    self.assertEqual( 'bar', next(it) )
    self.assertEqual( 'apple', next(it) )
    self.assertEqual( 'kiwi', next(it) )
    
  def test___eq__(self):
    a = SL()
    a.append('foo')
    a.append('bar')

    b = SL()
    b.append('apple')
    b.append('kiwi')

    self.assertFalse( a == b )
    
    c = SL()
    c.append('foo')
    c.append('bar')

    self.assertTrue( a == c )

    self.assertEqual( a, [ 'foo', 'bar' ] )
    self.assertEqual( [ 'foo', 'bar' ], a )
    
  def xtest___cmp__(self):
    a = SL()
    a.append(KV('foo', 'hi'))
    a.append(KV('bar', '666'))

    b = SL()
    b.append(KV('apple', '6'))
    b.append(KV('kiwi', '7'))

    self.assertEqual( 1, cmp(a, b) )
    
    c = SL()
    c.append(KV('foo', 'hi'))
    c.append(KV('bar', '666'))

    self.assertEqual( 0, cmp(a, c) )

  def xtest_remove(self):
    l = SL()
    l.append(KV('foo', 'hi'))
    l.append(KV('bar', '666'))
    self.assertEqual( 2, len(l) )
    self.assertEqual( KV('foo', 'hi'), l[0] )
    self.assertEqual( KV('bar', '666'), l[1] )

    l.remove(KV('bar', '666'))

    self.assertEqual( 1, len(l) )
    self.assertEqual( KV('foo', 'hi'), l[0] )
    
  def xtest_remove_key(self):
    l = SL()
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

  def xtest_find_key_value(self):
    l = SL()
    l.append(KV('foo', 'hi'))
    l.append(KV('bar', '666'))

    found = l.find_key_value(KV('foo', 'hi'))
    self.assertEqual( KV('foo', 'hi'), found )
    
    found = l.find_key_value(KV('foo', 'not'))
    self.assertEqual( None, found )
    
  def xtest_find_key(self):
    l = SL()
    l.append(KV('foo', 'hi'))
    l.append(KV('bar', '666'))

    found = l.find_key('foo')
    self.assertEqual( KV('foo', 'hi'), found )
    
    found = l.find_key('not')
    self.assertEqual( None, found )
    
  def xtest_find_all_key(self):
    l = SL()
    l.append(KV('foo', 'hi'))
    l.append(KV('bar', '666'))
    l.append(KV('foo', 'hi2'))

    found = l.find_all_key('foo')
    self.assertEqual( [ KV('foo', 'hi'), KV('foo', 'hi2') ], found )
    
  def xtest_is_homogeneous(self):
    l1 = SL()
    l1.append(KV('foo', 666))
    l1.append(KV('bar', 667))
    l1.append(KV('foo', 668))
    self.assertEqual( True, l1.is_homogeneous(compat.STRING_TYPES, compat.INTEGER_TYPES) )

    l2 = SL()
    l2.append(KV('foo', 666))
    l2.append(KV('bar', '667'))
    l2.append(KV('foo', 668))
    self.assertEqual( False, l2.is_homogeneous(compat.STRING_TYPES, compat.INTEGER_TYPES) )
    
  def xtest_from_dict(self):
    self.assertEqual( SL([ KV('a', 5), KV('b', 6) ]), SL.from_dict({ 'a': 5, 'b': 6 }) )
    
if __name__ == "__main__":
  unit_test.main()

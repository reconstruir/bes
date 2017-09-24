#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

from bes.testing.unit_test import unit_test
from bes.key_value import key_value_list as KVL
from bes.key_value import key_value as KV

class test_key_value_list(unit_test):

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
    self.assertEqual( KV('foo', 'hi'), it.next() )
    self.assertEqual( KV('bar', '666'), it.next() )
    self.assertEqual( KV('apple', '6'), it.next() )
    self.assertEqual( KV('kiwi', '7'), it.next() )
    
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
    
  def test_find_key(self):
    l = KVL()
    l.append(KV('foo', 'hi'))
    l.append(KV('bar', '666'))

    found = l.find_key('foo')
    self.assertEqual( KV('foo', 'hi'), found )
    
    found = l.find_key('not')
    self.assertEqual( None, found )
    
  def test_find_all_key(self):
    l = KVL()
    l.append(KV('foo', 'hi'))
    l.append(KV('bar', '666'))
    l.append(KV('foo', 'hi2'))

    found = l.find_all_key('foo')
    self.assertEqual( [ KV('foo', 'hi'), KV('foo', 'hi2') ], found )
    
if __name__ == "__main__":
  unit_test.main()

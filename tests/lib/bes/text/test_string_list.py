#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.text.string_list import string_list as SL
from bes.system.compat import compat
from bes.compat.cmp import cmp

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
    
  def test___cmp__(self):
    a = SL()
    a.append('foo')
    a.append('bar')

    b = SL()
    b.append('apple')
    b.append('kiwi')

    self.assertEqual( 1, cmp(a, b) )
    
    c = SL()
    c.append('foo')
    c.append('bar')

    self.assertEqual( 0, cmp(a, c) )

  def test_remove(self):
    l = SL()
    l.append('foo')
    l.append('bar')
    self.assertEqual( 2, len(l) )
    self.assertEqual( 'foo', l[0] )
    self.assertEqual( 'bar', l[1] )

    l.remove('bar')

    self.assertEqual( 1, len(l) )
    self.assertEqual( 'foo', l[0] )

  def test_substitute_variables(self):
    l = SL([ 'a', 'a is ${foo}', 'b', 'b is ${bar}' ])
    l.substitute_variables({ 'foo': 'apple', 'bar': 'kiwi' })
    self.assertEqual( SL([ 'a', 'a is apple', 'b', 'b is kiwi' ]), l )
    
if __name__ == "__main__":
  unit_test.main()

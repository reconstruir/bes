#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.common import type_checked_list
from bes.system import compat
from bes.compat import cmp
from collections import namedtuple

class IL(type_checked_list):

  def __init__(self, values = None):
    super(IL, self).__init__(compat.INTEGER_TYPES, values = values)

class test_type_checked_list(unit_test):

  def test___init__with_tuples(self):
    l = IL( ( 5, 6 ) )
    self.assertEqual( 2, len(l) )
    self.assertEqual( 5, l[0] )
    self.assertEqual( 6, l[1] )
    
  def test_append(self):
    l = IL()
    l.append(5)
    self.assertEqual( 1, len(l) )
    
  def test_to_string(self):
    l = IL()
    l.append(5)
    l.append(6)
    self.assertEqual( '[5, 6]', str(l) )
    
  def test_contains(self):
    l = IL()
    l.append(5)
    l.append(6)
    self.assertTrue( 5 in l )
    self.assertTrue( 6 in l )
    self.assertFalse( 7 in l )
    
  def test_add(self):
    a = IL()
    a.append(5)
    a.append(6)

    b = IL()
    b.append(7)
    b.append(8)

    c = a + b
    self.assertEqual( 4, len(c) )
    it = iter(c)
    self.assertEqual( 5, next(it) )
    self.assertEqual( 6, next(it) )
    self.assertEqual( 7, next(it) )
    self.assertEqual( 8, next(it) )
    
  def test___eq__(self):
    a = IL()
    a.append(5)
    a.append(6)

    b = IL()
    b.append(7)
    b.append(8)

    self.assertFalse( a == b )
    
    c = IL()
    c.append(5)
    c.append(6)

    self.assertTrue( a == c )

    self.assertEqual( a, [ 5, 6 ] )
    self.assertEqual( a, ( 5, 6 ) )
    self.assertEqual( [ 5, 6 ], a )
    self.assertEqual( ( 5, 6 ), a )
    
  def test___cmp__(self):
    a = IL()
    a.append(5)
    a.append(6)

    b = IL()
    b.append(7)
    b.append(8)

    self.assertEqual( -1, a.compare(b) )
    
    c = IL()
    c.append(5)
    c.append(6)

    self.assertEqual( 0, a.compare(c) )

  def test_remove(self):
    l = IL()
    l.append(5)
    l.append(6)
    self.assertEqual( 2, len(l) )
    self.assertEqual( 5, l[0] )
    self.assertEqual( 6, l[1] )

    l.remove(5)

    self.assertEqual( 1, len(l) )
    self.assertEqual( 6, l[0] )
    
  def test_sort(self):
    T = namedtuple('T', 'a,b')
    class TL(type_checked_list):
      def __init__(self, values = None):
        super(TL, self).__init__(T, values = values)
    l = TL([ T('apple', 6), T('pear', 1), T('kiwi', 7) ])
    self.assertEqual( [ T('apple', 6), T('pear', 1), T('kiwi', 7) ], [ x for x in l ] )
    l.sort()
    self.assertEqual( [ T('apple', 6), T('kiwi', 7), T('pear', 1) ], [ x for x in l ] )
    l.sort(key = lambda x: x.b)
    self.assertEqual( [ T('pear', 1), T('apple', 6), T('kiwi', 7) ], [ x for x in l ] )
    l = TL([ T('apple', 6), T('pear', 1), T('kiwi', 7) ])
    l.sort(cmp = lambda a, b: cmp(a.a[-1], b.a[-1]))
    self.assertEqual( [ T('apple', 6), T('kiwi', 7), T('pear', 1) ], [ x for x in l ] )
    
if __name__ == "__main__":
  unit_test.main()

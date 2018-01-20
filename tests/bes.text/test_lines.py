#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.text import lines

class test_lines(unit_test):

  def test_empty(self):
    l = lines('')
    self.assertEqual( 1, len(l) )

  def test_1_line(self):
    l = lines('foo')
    self.assertEqual( 1, len(l) )
    self.assertEqual( 'foo', l[0] )
    
  def test_1_line_with_newline(self):
    l = lines('foo\n')
    self.assertEqual( 2, len(l) )
    self.assertEqual( 'foo', l[0] )
    self.assertEqual( '', l[1] )
    
  def test_1_empty_line(self):
    l = lines('\n')
    self.assertEqual( 2, len(l) )
    self.assertEqual( '', l[0] )
    self.assertEqual( '', l[1] )
    
  def test_basic(self):
    l = lines('foo bar\napple kiwi')
    self.assertEqual( 2, len(l) )
    self.assertEqual( 'foo bar', l[0] )
    self.assertEqual( 'apple kiwi', l[1] )
    
  def test___setitem__(self):
    l = lines('foo bar\napple kiwi')
    with self.assertRaises(RuntimeError) as context:
      l[0] = 'foo'
    
if __name__ == '__main__':
  unit_test.main()

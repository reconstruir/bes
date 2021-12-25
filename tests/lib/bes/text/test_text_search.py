#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.text.text_search import text_search
from bes.testing.unit_test import unit_test

class test_text_search(unit_test):

  def test_find_all(self):
    self.assertEqual( [
      ( 0, 2 ),
      ( 12, 14 ),
      ( 20, 22 ),
    ], text_search.find_all('foo and bar foo and foo', 'foo') )
#    self.assertEqual( [], f('bar', 'foo') )
#    self.assertEqual( [ 0 ], f('foo', 'foo') )
#    self.assertEqual( [ 4, 16 ], f('foo and bar foo and foo', 'and') )
'''
  def test_replace_span(self):
    f = SU.replace_span
    self.assertEqual( 'foo & bar foo and foo', f('foo and bar foo and foo', 4, 3, '&', word_boundary = False) )
    self.assertEqual( 'xoo', f('foo', 0, 1, 'x', word_boundary = False) )
    self.assertEqual( 'fxo', f('foo', 1, 1, 'x', word_boundary = False) )
    self.assertEqual( 'fox', f('foo', 2, 1, 'x', word_boundary = False) )

    with self.assertRaises(ValueError) as ctx:
      f('foo', 3, 1, 'x')
    with self.assertRaises(ValueError) as ctx:
      f('foo', -1, 1, 'x')
    with self.assertRaises(ValueError) as ctx:
      f('foo', 0, 0, 'x')

  def test_replace_span_with_word_boundary(self):
    f = SU.replace_span
    self.assertEqual( 'foo.&:bar', f('foo.and:bar', 4, 3, '&', word_boundary = True) )
    self.assertEqual( 'fooxandybar', f('fooxandybar', 4, 3, '&', word_boundary = True) )
    self.assertEqual( 'x', f('foo', 0, 3, 'x', word_boundary = True) )
    self.assertEqual( 'foo_', f('foo_', 0, 3, 'x', word_boundary = True) )
    self.assertEqual( '_foo', f('_foo', 1, 3, 'x', word_boundary = True) )

  def test_replace_span_with_word_boundary_and_underscore(self):
    f = SU.replace_span
    self.assertEqual( 'x', f('foo', 0, 3, 'x', word_boundary = True, underscore = True) )
    self.assertEqual( 'x_', f('foo_', 0, 3, 'x', word_boundary = True, underscore = True) )
    self.assertEqual( '_x', f('_foo', 1, 3, 'x', word_boundary = True, underscore = True) )
    
  def test_replace_all(self):
    f = SU.replace_all
    self.assertEqual( 'foo & bar foo & foo', f('foo and bar foo and foo', 'and', '&', word_boundary = False) )
    self.assertEqual( 'foo and bar foo and foo', f('foo and bar foo and foo', 'kiwi', '&', word_boundary = False) )
    self.assertEqual( 'fxx', f('foo', 'o', 'x', word_boundary = False) )
    self.assertEqual( 'foo', f('foo', 'o', 'o', word_boundary = False) )
    self.assertEqual( 'fxxxx', f('foo', 'o', 'xx', word_boundary = False) )
    self.assertEqual( 'foooo', f('foo', 'o', 'oo', word_boundary = False) )

  def test_replace_all_with_word_boundary(self):
    f = SU.replace_all
    self.assertEqual( 'foo & bar foo & foo', f('foo and bar foo and foo', 'and', '&', word_boundary = True) )
    self.assertEqual( 'foo and bar foo and foo', f('foo and bar foo and foo', 'kiwi', '&', word_boundary = True) )
    self.assertEqual( 'foo', f('foo', 'o', 'x', word_boundary = True) )
    self.assertEqual( 'foo', f('foo', 'o', 'o', word_boundary = True) )
    self.assertEqual( 'foo', f('foo', 'o', 'xx', word_boundary = True) )
    self.assertEqual( 'foo', f('foo', 'o', 'oo', word_boundary = True) )
    self.assertEqual( 'o', f('foo', 'foo', 'o', word_boundary = True) )
'''    
if __name__ == '__main__':
  unit_test.main()

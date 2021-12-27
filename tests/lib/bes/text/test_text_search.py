#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import OrderedDict
from bes.text.text_search import text_search
from bes.testing.unit_test import unit_test

class test_text_search(unit_test):

  def test_find_all(self):
    self.assertEqual( [
      ( 0, 2 ),
      ( 12, 14 ),
      ( 20, 22 ),
    ], text_search.find_all('foo and bar foo and foo', 'foo') )

  def test_find_all_word_boundary(self):
    self.assertEqual( [
      ( 12, 14 ),
    ], text_search.find_all('foo1and bar foo and fooy', 'foo', word_boundary = True) )

  def test_replace_span(self):
    f = text_search.replace_span
    self.assertEqual( 'foo & bar foo and foo', f('foo and bar foo and foo', 4, 6, '&') )
    self.assertEqual( 'xoo', f('foo', 0, 0, 'x') )
    self.assertEqual( 'fxo', f('foo', 1, 1, 'x') )
    self.assertEqual( 'fox', f('foo', 2, 2, 'x') )

    with self.assertRaises(ValueError) as ctx:
      f('foo', 3, 1, 'x')
    with self.assertRaises(ValueError) as ctx:
      f('foo', -1, 1, 'x')
    with self.assertRaises(ValueError) as ctx:
      f('foo', 1, 0, 'x')

  def test_replace_all(self):
    f = text_search.replace_all
    self.assertEqual( 'this is nothing!', f('this is nothing!', 'foo', 'kiwi', word_boundary = False) )
    self.assertEqual( 'foo & bar foo & foo', f('foo and bar foo and foo', 'and', '&', word_boundary = False) )
    self.assertEqual( 'foo and bar foo and foo', f('foo and bar foo and foo', 'kiwi', '&', word_boundary = False) )
    self.assertEqual( 'fxx', f('foo', 'o', 'x', word_boundary = False) )
    self.assertEqual( 'foo', f('foo', 'o', 'o', word_boundary = False) )
    self.assertEqual( 'fxxxx', f('foo', 'o', 'xx', word_boundary = False) )
    self.assertEqual( 'foooo', f('foo', 'o', 'oo', word_boundary = False) )
    self.assertEqual( 'kiwi', f('foo', 'foo', 'kiwi', word_boundary = False) )
    self.assertEqual( 'kiwi ', f('foo ', 'foo', 'kiwi', word_boundary = False) )

  def test_replace_all_with_word_boundary(self):
    f = text_search.replace_all
    self.assertEqual( 'foo & bar foo & foo', f('foo and bar foo and foo', 'and', '&', word_boundary = True) )
    self.assertEqual( 'foo and bar foo and foo', f('foo and bar foo and foo', 'kiwi', '&', word_boundary = True) )
    self.assertEqual( 'foo', f('foo', 'o', 'x', word_boundary = True) )
    self.assertEqual( 'foo', f('foo', 'o', 'o', word_boundary = True) )
    self.assertEqual( 'foo', f('foo', 'o', 'xx', word_boundary = True) )
    self.assertEqual( 'foo', f('foo', 'o', 'oo', word_boundary = True) )
    self.assertEqual( 'o', f('foo', 'foo', 'o', word_boundary = True) )

  def test_replace_punctuation(self):
    f = text_search.replace_punctuation
    self.assertEqual( 'foo', f('foo', None) )
    self.assertEqual( 'foo', f('foo!', None) )
    self.assertEqual( 'foo1', f('foo!', '1') )
    self.assertEqual( 'foo bar', f('foo,bar', ' ') )

  def test_replace_white_space(self):
    f = text_search.replace_white_space
    self.assertEqual( 'a b c', f('a   b   c', ' ') )
    self.assertEqual( 'a b c', f('a b c', ' ') )
    self.assertEqual( 'a b c', f('a  b  c', ' ') )
    self.assertEqual( ' a b c', f(' a  b  c', ' ') )
    self.assertEqual( ' a b c', f('  a  b  c', ' ') )
    self.assertEqual( 'a b c ', f('a   b   c ', ' ') )
    self.assertEqual( 'a b c ', f('a   b   c  ', ' ') )
    self.assertEqual( 'a b c ', f('a   b   c   ', ' ') )
    self.assertEqual( 'a_b_c_', f('a   b   c   ', '_') )
    self.assertEqual( '_a_b_c_', f(' a   b   c   ', '_') )

  def test_replace(self):
    f = text_search.replace
    self.assertEqual( 'foo bar',
                      f('a b', { 'a': 'foo', 'b': 'bar' }) )
    self.assertEqual( 'foo foond bar barut not foobarfoo',
                      f('a and b but not aba', { 'a': 'foo', 'b': 'bar' }, word_boundary = False) )


    
  def test_replace_with_word_boundary(self):
    f = text_search.replace
    self.assertEqual( 'apple and bar but not aba',
                      f('a and b but not aba', { 'a': 'apple', 'b': 'bar' }, word_boundary = True) )
    self.assertEqual( 'applebar', f('applebar', { 'apple': 'kiwi' }, word_boundary = True) )
    self.assertEqual( 'apple_bar', f('apple_bar', { 'apple': 'kiwi' }, word_boundary = True) )
    self.assertEqual( '1apple', f('1apple', { 'apple': 'kiwi' }, word_boundary = True) )
    self.assertEqual( 'apple1', f('apple1', { 'apple': 'kiwi' }, word_boundary = True) )
    self.assertEqual( 'kiwi.', f('apple.', { 'apple': 'kiwi' }, word_boundary = True) )
    self.assertEqual( 'kiwi', f('apple', { 'apple': 'kiwi' }, word_boundary = True) )
    self.assertEqual( ' kiwi', f(' apple', { 'apple': 'kiwi' }, word_boundary = True) )
    self.assertEqual( 'kiwi ', f('apple ', { 'apple': 'kiwi' }, word_boundary = True) )

  def test_replace_dependency(self):
    f = text_search.replace
    r = OrderedDict({
      'ziwi': 'kiwi',
      'kiwi': 'apple',
      'apple': 'lemon',
      'lemon': 'potato',
    })
    self.assertEqual( 'potato', f('ziwi', r) )
    
  def xtest_replace_with_word_boundary_and_underscore(self):
    f = text_search.replace
    self.assertEqual( 'applebar', f('applebar', { 'apple': 'kiwi' }, word_boundary = True, underscore = True) )
    self.assertEqual( 'kiwi_bar', f('apple_bar', { 'apple': 'kiwi' }, word_boundary = True, underscore = True) )
    
  def test_replace_many_parts(self):
    f = text_search.replace
    r = OrderedDict({
      'kiwi': 'ea',
      'lemon-CookingTogether': 'bk',
      'potato-Escaperoom': 'hp',
      'coffee': 'im',
      'butter-EscapeRoom': 'tc',
    })
    self.assertEqual( 'prefix_support-ea-abcdef0_lemon-park-0.6.51_potato-pond-0.154_im-abcdef0_butter-pond-0.3.46',
                      f('prefix_support-kiwi-abcdef0_lemon-park-0.6.51_potato-pond-0.154_coffee-abcdef0_butter-pond-0.3.46', r, word_boundary = False) )

  def xtest_replace_escaped(self):
    self.assertEqual( 'foo c:\\tmp bar', f('foo ${root_dir} bar', { '${root_dir}': 'c:\\tmp' }) )
    self.assertEqual( 'fooc:\\tmpbar', f('foo${root_dir}bar', { '${root_dir}': 'c:\\tmp' }) )
    
    
if __name__ == '__main__':
  unit_test.main()

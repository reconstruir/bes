#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import unittest
from bes.common.string_util import string_util as SU

class test_string_util(unittest.TestCase):

  def test_replace_white_space(self):
    self.assertEqual( 'a b c', SU.replace_white_space('a   b   c', ' ') )
    self.assertEqual( 'a b c', SU.replace_white_space('a b c', ' ') )
    self.assertEqual( 'a b c', SU.replace_white_space('a  b  c', ' ') )
    self.assertEqual( ' a b c', SU.replace_white_space(' a  b  c', ' ') )
    self.assertEqual( ' a b c', SU.replace_white_space('  a  b  c', ' ') )
    self.assertEqual( 'a b c ', SU.replace_white_space('a   b   c ', ' ') )
    self.assertEqual( 'a b c ', SU.replace_white_space('a   b   c  ', ' ') )
    self.assertEqual( 'a b c ', SU.replace_white_space('a   b   c   ', ' ') )
    self.assertEqual( 'a_b_c_', SU.replace_white_space('a   b   c   ', '_') )
    self.assertEqual( '_a_b_c_', SU.replace_white_space(' a   b   c   ', '_') )

  def test_split_by_white_space(self):
    self.assertEqual( [ 'a', 'b', 'c' ], SU.split_by_white_space('a b c') )
    self.assertEqual( [ 'a', 'b', 'c' ], SU.split_by_white_space(' a b c') )
    self.assertEqual( [ 'a', 'b', 'c' ], SU.split_by_white_space(' a b c ') )
    self.assertEqual( [ 'a', 'b', 'c' ], SU.split_by_white_space(' a b  c ') )
    self.assertEqual( [], SU.split_by_white_space('') )
    self.assertEqual( ['a'], SU.split_by_white_space('a') )

  def test_remove_tail(self):
    self.assertEqual( 'fo', SU.remove_tail('foobar', [ 'bar', 'o' ]) )

  def test_remove_tail(self):
    self.assertEqual( 'foo', SU.remove_tail('foo.tar.gz', [ '.tar.gz' ]) )
    self.assertEqual( 'foo', SU.remove_tail('foo.tar.gz', '.tar.gz') )
    self.assertEqual( 'foo', SU.remove_tail('foo.tar.gz', [ '.gz', '.tar' ]) )

  def test_remove_head(self):
    self.assertEqual( 'ar', SU.remove_head('foobar', [ 'foo', 'b' ]) )

  def test_replace(self):
    self.assertEqual( 'foo bar', SU.replace('a b', { 'a': 'foo', 'b': 'bar' }) )

  def test_replace_with_word_boundary(self):
    self.assertEqual( 'apple and bar but not aba',
                      SU.replace('a and b but not aba', { 'a': 'apple', 'b': 'bar' }, word_boundary = True) )
    self.assertEqual( 'applebar', SU.replace('applebar', { 'apple': 'kiwi' }, word_boundary = True) )
    self.assertEqual( 'apple_bar', SU.replace('apple_bar', { 'apple': 'kiwi' }, word_boundary = True) )
    self.assertEqual( '1apple', SU.replace('1apple', { 'apple': 'kiwi' }, word_boundary = True) )
    self.assertEqual( 'apple1', SU.replace('apple1', { 'apple': 'kiwi' }, word_boundary = True) )
    self.assertEqual( 'kiwi.', SU.replace('apple.', { 'apple': 'kiwi' }, word_boundary = True) )
    self.assertEqual( 'kiwi', SU.replace('apple', { 'apple': 'kiwi' }, word_boundary = True) )
    self.assertEqual( ' kiwi', SU.replace(' apple', { 'apple': 'kiwi' }, word_boundary = True) )
    self.assertEqual( 'kiwi ', SU.replace('apple ', { 'apple': 'kiwi' }, word_boundary = True) )

  def test_replace_with_word_boundary_and_underscore(self):
    self.assertEqual( 'applebar', SU.replace('applebar', { 'apple': 'kiwi' }, word_boundary = True, underscore = True) )
    self.assertEqual( 'kiwi_bar', SU.replace('apple_bar', { 'apple': 'kiwi' }, word_boundary = True, underscore = True) )
    
  def test_replace_no_word_boundary(self):
    self.assertEqual( 'foo foond bar barut not foobarfoo', SU.replace('a and b but not aba', { 'a': 'foo', 'b': 'bar' }, word_boundary = False) )

  def xtest_replace_escaped(self):
    self.assertEqual( 'foo c:\\tmp bar', SU.replace('foo ${root_dir} bar', { '${root_dir}': 'c:\\tmp' }) )
    self.assertEqual( 'fooc:\\tmpbar', SU.replace('foo${root_dir}bar', { '${root_dir}': 'c:\\tmp' }) )
    
  def test_flatten(self):
    self.assertEqual( 'foo bar', SU.flatten('foo bar') )
    self.assertEqual( 'foo bar', SU.flatten(['foo', 'bar']) )

  def test_is_string(self):
    self.assertEqual( True, SU.is_string('foo') )
    self.assertEqual( True, SU.is_string(u'foo') )
    self.assertEqual( True, SU.is_string(r'foo') )
    self.assertEqual( False, SU.is_string(['foo']) )
    self.assertEqual( False, SU.is_string(False) )

  def test_is_char(self):
    self.assertEqual( True, SU.is_char('a') )
    self.assertEqual( True, SU.is_char(u'a') )
    self.assertEqual( False, SU.is_char('foo') )
    self.assertEqual( False, SU.is_char('') )
    self.assertEqual( False, SU.is_char(1) )

  def test_unquote(self):
    self.assertEqual( 'foo', SU.unquote('\'foo\'') )
    self.assertEqual( 'foo', SU.unquote('\"foo\"') )
    self.assertEqual( '\'foo\"', SU.unquote('\'foo\"') )
    self.assertEqual( '\'foo', SU.unquote('\'foo') )
    self.assertEqual( 'foo\'', SU.unquote('foo\'') )

  def test_quote(self):
    self.assertEqual( '"foo"', SU.quote('foo') )
    self.assertEqual( '\'foo\'', SU.quote('foo', quote_char = "'") )
    self.assertEqual( '\'fo"o\'', SU.quote('fo"o') )
    self.assertEqual( '"fo\'o"', SU.quote('fo\'o') )
    self.assertEqual( '"foo"', SU.quote('"foo"') )
    self.assertEqual( '\'foo\'', SU.quote('\'foo\'') )
    self.assertEqual( '\'foo\'', SU.quote('"foo"', quote_char = "'") )
    self.assertEqual( '\'foo\'', SU.quote('\'foo\'', quote_char = "'") )
    self.assertEqual( '\"foo\"', SU.quote('"foo"', quote_char = '"') )
    self.assertEqual( '\"foo\"', SU.quote('\'foo\'', quote_char = '"') )

  def test_is_quoted(self):
    self.assertEqual( True, SU.is_quoted('\'foo\'') )
    self.assertEqual( True, SU.is_quoted('\"foo\"') )
    self.assertEqual( False, SU.is_quoted('\'foo\"') )
    self.assertEqual( False, SU.is_quoted('\'foo') )
    self.assertEqual( False, SU.is_quoted('foo\'') )
    self.assertEqual( False, SU.is_quoted('f"o"o') )

  def test_is_single_quoted(self):
    self.assertEqual( True, SU.is_single_quoted('\'foo\'') )
    self.assertEqual( False, SU.is_single_quoted('\"foo\"') )

  def test_is_double_quoted(self):
    self.assertEqual( False, SU.is_double_quoted('\'foo\'') )
    self.assertEqual( True, SU.is_double_quoted('\"foo\"') )

  def test_left_justify(self):
    self.assertEqual( 'foo   ', SU.left_justify('foo', 6, ' ') )

  def test_right_justify(self):
    self.assertEqual( '   foo', SU.right_justify('foo', 6, ' ') )

  def test_has_white_space(self):
    self.assertEqual( False, SU.has_white_space('foo') )
    self.assertEqual( True, SU.has_white_space(' foo') )
    self.assertEqual( True, SU.has_white_space('f oo') )
    self.assertEqual( True, SU.has_white_space('f oo ') )
    self.assertEqual( True, SU.has_white_space(r'f\ oo') )

  def test_reversed(self):
    self.assertEqual( 'oof', SU.reverse('foo') )

  def test_strip_ends(self):
    self.assertEqual( ' foo ', SU.strip_ends(' foo ') )
    self.assertEqual( 'foo ', SU.strip_ends(' foo ', strip_head = True) )
    self.assertEqual( ' foo', SU.strip_ends(' foo ', strip_tail = True) )
    self.assertEqual( 'foo', SU.strip_ends(' foo ', strip_head = True, strip_tail = True) )

  def test_replace_punctuation(self):
    f = SU.replace_punctuation
    self.assertEqual( 'foo', f('foo', None) )
    self.assertEqual( 'foo', f('foo!', None) )
    self.assertEqual( 'foo1', f('foo!', '1') )
    self.assertEqual( 'foo bar', f('foo,bar', ' ') )

  def test_partition_by_white_space(self):
    f = SU.partition_by_white_space
    self.assertEqual( ( 'a', ' ', 'b' ), f('a b') )
    self.assertEqual( ( 'a', '  ', 'b' ), f('a  b') )
    self.assertEqual( ( 'a', ' ', 'b  c' ), f('a b  c') )
    self.assertEqual( ( 'a', ' ', 'b  c' ), f('a b  c') )
    self.assertEqual( ( 'a', ' ', 'b  c ' ), f('a b  c ') )
    self.assertEqual( ( 'a', ' ', 'b  c' ), f('a b  c ', strip = True) )

  def test_insert(self):
    f = SU.insert
    self.assertEqual( 'foo', f('foo', '', 0) )
    self.assertEqual( 'foo', f('foo', '', 1) )
    self.assertEqual( 'foo', f('foo', '', 2) )
    self.assertEqual( 'foo', f('foo', '', 3) )
    self.assertEqual( 'foo', f('foo', '', 4) )

    self.assertEqual( '_foo', f('foo', '_', 0) )
    self.assertEqual( 'f_oo', f('foo', '_', 1) )
    self.assertEqual( 'fo_o', f('foo', '_', 2) )
    self.assertEqual( 'foo_', f('foo', '_', 3) )
    self.assertEqual( 'foo_', f('foo', '_', 4) )

    self.assertEqual( 'fo_o', f('foo', '_', -1) )
    self.assertEqual( 'f_oo', f('foo', '_', -2) )
    self.assertEqual( '_foo', f('foo', '_', -3) )
    self.assertEqual( '_foo', f('foo', '_', -4) )

  def test_replace_many_parts(self):
    f = SU.replace
    r = {
      'kiwi': 'ea',
      'lemon-CookingTogether': 'bk',
      'potato-Escaperoom': 'hp',
      'coffee': 'im',
      'butter-EscapeRoom': 'tc',
    }

    self.assertEqual( 'prefix_support-ea-abcdef0_lemon-park-0.6.51_potato-pond-0.154_im-abcdef0_butter-pond-0.3.46',
                      f('prefix_support-kiwi-abcdef0_lemon-park-0.6.51_potato-pond-0.154_coffee-abcdef0_butter-pond-0.3.46', r, word_boundary = False) )

  def test_find_all(self):
    def f(s, sub_string):
      return [ x for x in SU.find_all(s, sub_string) ]
    self.assertEqual( [ 0, 12, 20 ], f('foo and bar foo and foo', 'foo') )
    self.assertEqual( [], f('bar', 'foo') )
    self.assertEqual( [ 0 ], f('foo', 'foo') )
    self.assertEqual( [ 4, 16 ], f('foo and bar foo and foo', 'and') )

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
    
if __name__ == "__main__":
  unittest.main()

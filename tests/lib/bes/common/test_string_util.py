#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import unittest
from bes.common import string_util

class test_string_util(unittest.TestCase):

  def test_replace_white_space(self):
    self.assertEqual( 'a b c', string_util.replace_white_space('a   b   c', ' ') )
    self.assertEqual( 'a b c', string_util.replace_white_space('a b c', ' ') )
    self.assertEqual( 'a b c', string_util.replace_white_space('a  b  c', ' ') )
    self.assertEqual( ' a b c', string_util.replace_white_space(' a  b  c', ' ') )
    self.assertEqual( ' a b c', string_util.replace_white_space('  a  b  c', ' ') )
    self.assertEqual( 'a b c ', string_util.replace_white_space('a   b   c ', ' ') )
    self.assertEqual( 'a b c ', string_util.replace_white_space('a   b   c  ', ' ') )
    self.assertEqual( 'a b c ', string_util.replace_white_space('a   b   c   ', ' ') )
    self.assertEqual( 'a_b_c_', string_util.replace_white_space('a   b   c   ', '_') )
    self.assertEqual( '_a_b_c_', string_util.replace_white_space(' a   b   c   ', '_') )

  def test_split_by_white_space(self):
    self.assertEqual( [ 'a', 'b', 'c' ], string_util.split_by_white_space('a b c') )
    self.assertEqual( [ 'a', 'b', 'c' ], string_util.split_by_white_space(' a b c') )
    self.assertEqual( [ 'a', 'b', 'c' ], string_util.split_by_white_space(' a b c ') )
    self.assertEqual( [ 'a', 'b', 'c' ], string_util.split_by_white_space(' a b  c ') )
    self.assertEqual( [], string_util.split_by_white_space('') )
    self.assertEqual( ['a'], string_util.split_by_white_space('a') )

  def test_remove_tail(self):
    self.assertEqual( 'fo', string_util.remove_tail('foobar', [ 'bar', 'o' ]) )

  def test_remove_head(self):
    self.assertEqual( 'ar', string_util.remove_head('foobar', [ 'foo', 'b' ]) )

  def test_replace(self):
    self.assertEqual( 'foo bar', string_util.replace('a b', { 'a': 'foo', 'b': 'bar' }) )

  def test_replace_word_boundary(self):
    self.assertEqual( 'foo and bar but not aba', string_util.replace('a and b but not aba', { 'a': 'foo', 'b': 'bar' }) )

  def test_replace_dont_word_boundary(self):
    self.assertEqual( 'foo foond bar barut not foobarfoo', string_util.replace('a and b but not aba', { 'a': 'foo', 'b': 'bar' }, word_boundary = False) )

  def test_flatten(self):
    self.assertEqual( 'foo bar', string_util.flatten('foo bar') )
    self.assertEqual( 'foo bar', string_util.flatten(['foo', 'bar']) )

  def test_is_string(self):
    self.assertEqual( True, string_util.is_string('foo') )
    self.assertEqual( True, string_util.is_string(u'foo') )
    self.assertEqual( True, string_util.is_string(r'foo') )
    self.assertEqual( False, string_util.is_string(['foo']) )
    self.assertEqual( False, string_util.is_string(False) )

  def test_is_char(self):
    self.assertEqual( True, string_util.is_char('a') )
    self.assertEqual( True, string_util.is_char(u'a') )
    self.assertEqual( False, string_util.is_char('foo') )
    self.assertEqual( False, string_util.is_char('') )
    self.assertEqual( False, string_util.is_char(1) )

  def test_unquote(self):
    self.assertEqual( 'foo', string_util.unquote('\'foo\'') )
    self.assertEqual( 'foo', string_util.unquote('\"foo\"') )
    self.assertEqual( '\'foo\"', string_util.unquote('\'foo\"') )
    self.assertEqual( '\'foo', string_util.unquote('\'foo') )
    self.assertEqual( 'foo\'', string_util.unquote('foo\'') )

  def test_quote(self):
    self.assertEqual( '"foo"', string_util.quote('foo') )
    self.assertEqual( '\'foo\'', string_util.quote('foo', quote_char = "'") )
    self.assertEqual( '\'fo"o\'', string_util.quote('fo"o') )
    self.assertEqual( '"fo\'o"', string_util.quote('fo\'o') )
    self.assertEqual( '"foo"', string_util.quote('"foo"') )
    self.assertEqual( '\'foo\'', string_util.quote('\'foo\'') )
    self.assertEqual( '\'foo\'', string_util.quote('"foo"', quote_char = "'") )
    self.assertEqual( '\'foo\'', string_util.quote('\'foo\'', quote_char = "'") )
    self.assertEqual( '\"foo\"', string_util.quote('"foo"', quote_char = '"') )
    self.assertEqual( '\"foo\"', string_util.quote('\'foo\'', quote_char = '"') )

  def test_is_quoted(self):
    self.assertEqual( True, string_util.is_quoted('\'foo\'') )
    self.assertEqual( True, string_util.is_quoted('\"foo\"') )
    self.assertEqual( False, string_util.is_quoted('\'foo\"') )
    self.assertEqual( False, string_util.is_quoted('\'foo') )
    self.assertEqual( False, string_util.is_quoted('foo\'') )
    self.assertEqual( False, string_util.is_quoted('f"o"o') )

  def test_is_single_quoted(self):
    self.assertEqual( True, string_util.is_single_quoted('\'foo\'') )
    self.assertEqual( False, string_util.is_single_quoted('\"foo\"') )

  def test_is_double_quoted(self):
    self.assertEqual( False, string_util.is_double_quoted('\'foo\'') )
    self.assertEqual( True, string_util.is_double_quoted('\"foo\"') )

  def test_left_justify(self):
    self.assertEqual( 'foo   ', string_util.left_justify('foo', 6, ' ') )

  def test_right_justify(self):
    self.assertEqual( '   foo', string_util.right_justify('foo', 6, ' ') )

  def test_has_white_space(self):
    self.assertEqual( False, string_util.has_white_space('foo') )
    self.assertEqual( True, string_util.has_white_space(' foo') )
    self.assertEqual( True, string_util.has_white_space('f oo') )
    self.assertEqual( True, string_util.has_white_space('f oo ') )
    self.assertEqual( True, string_util.has_white_space('f\ oo') )

  def test_reversed(self):
    self.assertEqual( 'oof', string_util.reverse('foo') )

  def test_strip_ends(self):
    self.assertEqual( ' foo ', string_util.strip_ends(' foo ') )
    self.assertEqual( 'foo ', string_util.strip_ends(' foo ', strip_head = True) )
    self.assertEqual( ' foo', string_util.strip_ends(' foo ', strip_tail = True) )
    self.assertEqual( 'foo', string_util.strip_ends(' foo ', strip_head = True, strip_tail = True) )

  def test_replace_punctuation(self):
    f = string_util.replace_punctuation
    self.assertEqual( 'foo', f('foo', None) )
    self.assertEqual( 'foo', f('foo!', None) )
    self.assertEqual( 'foo1', f('foo!', '1') )
    self.assertEqual( 'foo bar', f('foo,bar', ' ') )

if __name__ == "__main__":
  unittest.main()

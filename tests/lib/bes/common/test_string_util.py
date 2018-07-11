#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import unittest
from bes.common import string_util as SU

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

  def test_remove_head(self):
    self.assertEqual( 'ar', SU.remove_head('foobar', [ 'foo', 'b' ]) )

  def test_replace(self):
    self.assertEqual( 'foo bar', SU.replace('a b', { 'a': 'foo', 'b': 'bar' }) )

  def test_replace_word_boundary(self):
    self.assertEqual( 'foo and bar but not aba', SU.replace('a and b but not aba', { 'a': 'foo', 'b': 'bar' }) )

  def test_replace_dont_word_boundary(self):
    self.assertEqual( 'foo foond bar barut not foobarfoo', SU.replace('a and b but not aba', { 'a': 'foo', 'b': 'bar' }, word_boundary = False) )

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
    self.assertEqual( True, SU.has_white_space('f\ oo') )

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

if __name__ == "__main__":
  unittest.main()

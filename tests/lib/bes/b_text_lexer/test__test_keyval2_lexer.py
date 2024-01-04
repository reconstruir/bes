#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os

from collections import namedtuple

from bes.testing.unit_test import unit_test

from _test_keyval2_lexer import _test_keyval2_lexer
from _test_lexer_mixin import _test_lexer_mixin

class test__test_keyval2_lexer(_test_lexer_mixin, unit_test):

  def test_empty_string(self):
    t = self._test_tokenize(_test_keyval2_lexer, '',
      [
        ( 't_done', '', ( 0, 0 ) ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  def test_just_key(self):
    t = self._test_tokenize(_test_keyval2_lexer, 'a',
      [
        ( 't_key', 'a', ( 1, 1 ) ),
        ( 't_done', '', ( 0, 0 ) ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )
    
  def test_just_key_and_equal(self):
    t = self._test_tokenize(_test_keyval2_lexer, 'ab=',
      [
        ( 't_key', 'ab', ( 1, 1 ) ),
        ( 't_equal', '=', ( 3, 1 ) ),
        ( 't_done', '', ( 0, 0 ) ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  def test_just_key_and_equal_with_trailing_white_space(self):
    t = self._test_tokenize(_test_keyval2_lexer, 'ab= ',
      [
        ( 't_key', 'ab', ( 1, 1 ) ),
        ( 't_equal', '=', ( 3, 1 ) ),
        ( 't_space', ' ', ( 4, 1 ) ),
        ( 't_done', '', ( 0, 0 ) ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )
    
  def test_key_and_value_short(self):
    t = self._test_tokenize(_test_keyval2_lexer, 'a=k',
      [
        ( 't_key', 'a', ( 1, 1 ) ),
        ( 't_equal', '=', ( 2, 1 ) ),
        ( 't_value', 'k', ( 3, 1 ) ),
        ( 't_done', '', ( 0, 0 ) ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  def test_key_and_value(self):
    t = self._test_tokenize(_test_keyval2_lexer, 'fruit=kiwi',
      [
        ( 't_key', 'fruit', ( 1, 1 ) ),
        ( 't_equal', '=', ( 6, 1 ) ),
        ( 't_value', 'kiwi', ( 7, 1 ) ),
        ( 't_done', '', ( 0, 0 ) ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  def test_key_and_value_with_trailing_space(self):
    t = self._test_tokenize(_test_keyval2_lexer, 'fruit=kiwi ',
      [
        ( 't_key', 'fruit', ( 1, 1 ) ),
        ( 't_equal', '=', ( 6, 1 ) ),
        ( 't_value', 'kiwi ', ( 7, 1 ) ),
        ( 't_done', '', ( 0, 0 ) ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  def test_key_and_value_with_multiple_trailing_space(self):
    t = self._test_tokenize(_test_keyval2_lexer, 'fruit=kiwi   ',
      [
        ( 't_key', 'fruit', ( 1, 1 ) ),
        ( 't_equal', '=', ( 6, 1 ) ),
        ( 't_value', 'kiwi   ', ( 7, 1 ) ),
        ( 't_done', '', ( 0, 0 ) ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )
    
  def test_one_space_before_key(self):
    t = self._test_tokenize(_test_keyval2_lexer, ' k=v',
      [
        ( 't_space', ' ', ( 1, 1 ) ),
        ( 't_key', 'k', ( 2, 1 ) ),
        ( 't_equal', '=', ( 3, 1 ) ),
        ( 't_value', 'v', ( 4, 1 ) ),
        ( 't_done', '', ( 0, 0 ) ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  def test_two_space_before_key(self):
    t = self._test_tokenize(_test_keyval2_lexer, '  k=v',
      [
        ( 't_space', '  ', ( 1, 1 ) ),
        ( 't_key', 'k', ( 3, 1 ) ),
        ( 't_equal', '=', ( 4, 1 ) ),
        ( 't_value', 'v', ( 5, 1 ) ),
        ( 't_done', '', ( 0, 0 ) ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  def test_two_tab_before_key(self):
    t = self._test_tokenize(_test_keyval2_lexer, '\t\tk=v',
      [
        ( 't_space', '\t\t', ( 1, 1 ) ),
        ( 't_key', 'k', ( 3, 1 ) ),
        ( 't_equal', '=', ( 4, 1 ) ),
        ( 't_value', 'v', ( 5, 1 ) ),
        ( 't_done', '', ( 0, 0 ) ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  def test_mixed_space_before_key(self):
    t = self._test_tokenize(_test_keyval2_lexer, '\t k=v',
      [
        ( 't_space', '\t ', ( 1, 1 ) ),
        ( 't_key', 'k', ( 3, 1 ) ),
        ( 't_equal', '=', ( 4, 1 ) ),
        ( 't_value', 'v', ( 5, 1 ) ),
        ( 't_done', '', ( 0, 0 ) ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  def test_one_space_after_key(self):
    t = self._test_tokenize(_test_keyval2_lexer, 'k =v',
      [
        ( 't_key', 'k', ( 1, 1 ) ),
        ( 't_space', ' ', ( 2, 1 ) ),
        ( 't_equal', '=', ( 3, 1 ) ),
        ( 't_value', 'v', ( 4, 1 ) ),
        ( 't_done', '', ( 0, 0 ) ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )
    
  def test_two_space_after_key(self):
    t = self._test_tokenize(_test_keyval2_lexer, 'k  =v',
      [
        ( 't_key', 'k', ( 1, 1 ) ),
        ( 't_space', '  ', ( 2, 1 ) ),
        ( 't_equal', '=', ( 4, 1 ) ),
        ( 't_value', 'v', ( 5, 1 ) ),
        ( 't_done', '', ( 0, 0 ) ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  def test_space_before_and_after_key(self):
    t = self._test_tokenize(_test_keyval2_lexer, '\t k \t=v',
      [
        ( 't_space', '\t ', ( 1, 1 ) ),
        ( 't_key', 'k', ( 3, 1 ) ),
        ( 't_space', ' \t', ( 4, 1 ) ),
        ( 't_equal', '=', ( 6, 1 ) ),
        ( 't_value', 'v', ( 7, 1 ) ),
        ( 't_done', '', ( 0, 0 ) ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  def test_one_space_before_value(self):
    t = self._test_tokenize(_test_keyval2_lexer, 'k= v',
      [
        ( 't_key', 'k', ( 1, 1 ) ),
        ( 't_equal', '=', ( 2, 1 ) ),
        ( 't_space', ' ', ( 3, 1 ) ),
        ( 't_value', 'v', ( 4, 1 ) ),
        ( 't_done', '', ( 0, 0 ) ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

    
  def test_multi_line(self):
    t = self._test_tokenize(_test_keyval2_lexer, '''
fruit=kiwi
color=green
''', 
      [
        ( 't_line_break', os.linesep, ( 1, 1 ) ),
        ( 't_key', 'fruit', ( 1, 2 ) ),
        ( 't_equal', '=', ( 6, 2 ) ),
        ( 't_value', 'kiwi', ( 7, 2 ) ),
        ( 't_line_break', os.linesep, ( 11, 2 ) ),
        ( 't_key', 'color', ( 1, 3 ) ),
        ( 't_equal', '=', ( 6, 3 ) ),
        ( 't_value', 'green', ( 7, 3 ) ),
        ( 't_line_break', os.linesep, ( 12, 3 ) ),
        ( 't_done', '', ( 0, 0 ) ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )
    
if __name__ == '__main__':
  unit_test.main()

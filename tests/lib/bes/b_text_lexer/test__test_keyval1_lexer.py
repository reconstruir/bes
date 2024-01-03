#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os

from bes.testing.unit_test import unit_test

from _test_keyval1_lexer import _test_keyval1_lexer
from _lexer_tester_mixin import _lexer_tester_mixin

class test__test_keyval1_lexer(_lexer_tester_mixin, unit_test):

  def test_empty_string(self):
    t = self._test_tokenize(_test_keyval1_lexer, '',
      [
        ( 't_done', '', ( 0, 0 ) ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  def test_just_key(self):
    t = self._test_tokenize(_test_keyval1_lexer, 'a',
      [
        ( 't_key', 'a', ( 1, 1 ) ),
        ( 't_done', '', ( 0, 0 ) ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )
    
  def test_just_key_and_equal(self):
    t = self._test_tokenize(_test_keyval1_lexer, 'ab=',
      [
        ( 't_key', 'ab', ( 1, 1 ) ),
        ( 't_equal', '=', ( 3, 1 ) ),
        ( 't_value', '', ( 3, 1 ) ),
        ( 't_done', '', ( 0, 0 ) ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  def test_key_and_value_short(self):
    t = self._test_tokenize(_test_keyval1_lexer, 'a=k',
      [
        ( 't_key', 'a', ( 1, 1 ) ),
        ( 't_equal', '=', ( 2, 1 ) ),
        ( 't_value', 'k', ( 3, 1 ) ),
        ( 't_done', '', ( 0, 0 ) ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  def test_key_and_value(self):
    t = self._test_tokenize(_test_keyval1_lexer, 'fruit=kiwi',
      [
        ( 't_key', 'fruit', ( 1, 1 ) ),
        ( 't_equal', '=', ( 6, 1 ) ),
        ( 't_value', 'kiwi', ( 7, 1 ) ),
        ( 't_done', '', ( 0, 0 ) ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  def xtest_one_space(self):
    t = self._test_tokenize(_test_keyval1_lexer, ' fruit=kiwi ',
      [
        ( 't_space', ' ', ( 1, 1 ) ),
        ( 't_key', 'fruit', ( 2, 1 ) ),
        ( 't_equal', '=', ( 7, 1 ) ),
        ( 't_value', 'kiwi', ( 8, 1 ) ),
        ( 't_space', ' ', ( 12, 1 ) ),
        ( 't_done', '', ( 0, 0 ) ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  def xtest_two_spaces(self):
    t = self._test_tokenize(_test_keyval1_lexer, '  fruit=kiwi  ',
      [
        ( 't_space', '  ', ( 1, 1 ) ),
        ( 't_key', 'fruit', ( 3, 1 ) ),
        ( 't_equal', '=', ( 8, 1 ) ),
        ( 't_value', 'kiwi', ( 9, 1 ) ),
        ( 't_space', '  ', ( 13, 1 ) ),
        ( 't_done', '', ( 0, 0 ) ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )
    
  def test_multi_line(self):
    t = self._test_tokenize(_test_keyval1_lexer, '''
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

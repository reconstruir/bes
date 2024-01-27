#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os

from bes.testing.unit_test import unit_test
from bes.btl.btl_lexer_tester_mixin import btl_lexer_tester_mixin

from _test_keyval1_lexer import _test_keyval1_lexer

class test__test_keyval1_lexer(btl_lexer_tester_mixin, unit_test):

  def test_empty_string(self):
    t = self.call_tokenize(_test_keyval1_lexer, '',
      [
        ( 't_done', None, None, 'h_done' ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  def test_just_key(self):
    t = self.call_tokenize(_test_keyval1_lexer, 'a',
      [
        ( 't_key', 'a', ( 1, 1 ), None ),
        ( 't_done', None, None, 'h_done' ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )
    
  def test_just_key_and_equal(self):
    t = self.call_tokenize(_test_keyval1_lexer, 'ab=',
      [
        ( 't_key', 'ab', ( 1, 1 ), None ),
        ( 't_equal', '=', ( 3, 1 ), None ),
        ( 't_value', '', ( 3, 1 ), None ),
        ( 't_done', None, None, 'h_done' ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  def test_key_and_value_short(self):
    t = self.call_tokenize(_test_keyval1_lexer, 'a=k',
      [
        ( 't_key', 'a', ( 1, 1 ), None ),
        ( 't_equal', '=', ( 2, 1 ), None ),
        ( 't_value', 'k', ( 3, 1 ), None ),
        ( 't_done', None, None, 'h_done' ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  def test_key_and_value(self):
    t = self.call_tokenize(_test_keyval1_lexer, 'fruit=kiwi',
      [
        ( 't_key', 'fruit', ( 1, 1 ), None ),
        ( 't_equal', '=', ( 6, 1 ), None ),
        ( 't_value', 'kiwi', ( 7, 1 ), None ),
        ( 't_done', None, None, 'h_done' ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  def xtest_one_space(self):
    t = self.call_tokenize(_test_keyval1_lexer, ' fruit=kiwi ',
      [
        ( 't_space', ' ', ( 1, 1 ), None ),
        ( 't_key', 'fruit', ( 2, 1 ), None ),
        ( 't_equal', '=', ( 7, 1 ), None ),
        ( 't_value', 'kiwi', ( 8, 1 ), None ),
        ( 't_space', ' ', ( 12, 1 ), None ),
        ( 't_done', None, None, 'h_done' ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  def xtest_two_spaces(self):
    t = self.call_tokenize(_test_keyval1_lexer, '  fruit=kiwi  ',
      [
        ( 't_space', '  ', ( 1, 1 ), None ),
        ( 't_key', 'fruit', ( 3, 1 ), None ),
        ( 't_equal', '=', ( 8, 1 ), None ),
        ( 't_value', 'kiwi', ( 9, 1 ), None ),
        ( 't_space', '  ', ( 13, 1 ), None ),
        ( 't_done', None, None, 'h_done' ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )
    
  def test_multi_line(self):
    t = self.call_tokenize(_test_keyval1_lexer, '''
fruit=kiwi
color=green
''', 
      [
        ( 't_line_break', os.linesep, ( 1, 1 ), 'h_line_break' ),
        ( 't_key', 'fruit', ( 1, 2 ), None ),
        ( 't_equal', '=', ( 6, 2 ), None ),
        ( 't_value', 'kiwi', ( 7, 2 ), None ),
        ( 't_line_break', os.linesep, ( 11, 2 ), 'h_line_break' ),
        ( 't_key', 'color', ( 1, 3 ), None ),
        ( 't_equal', '=', ( 6, 3 ), None ),
        ( 't_value', 'green', ( 7, 3 ), None ),
        ( 't_line_break', os.linesep, ( 12, 3 ), 'h_line_break' ),
        ( 't_done', None, None, 'h_done' ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

if __name__ == '__main__':
  unit_test.main()

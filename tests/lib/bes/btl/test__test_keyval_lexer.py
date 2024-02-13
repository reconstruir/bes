#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os

from collections import namedtuple

from bes.testing.unit_test import unit_test
from bes.btl.btl_lexer_tester_mixin import btl_lexer_tester_mixin

from _test_keyval_lexer import _test_keyval_lexer

class test__test_keyval_lexer(btl_lexer_tester_mixin, unit_test):

  def test_empty_string(self):
    t = self.call_lex_all(_test_keyval_lexer, '',
      [
        ( 't_done', None, None, 'h_done', None ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  def test_just_key(self):
    t = self.call_lex_all(_test_keyval_lexer, 'a',
      [
        ( 't_key', 'a', ( 1, 1 ), None, None ),
        ( 't_done', None, None, 'h_done', None ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )
    
  def test_just_key_and_equal(self):
    t = self.call_lex_all(_test_keyval_lexer, 'ab=',
      [
        ( 't_key', 'ab', ( 1, 1 ), None, None ),
        ( 't_key_value_delimiter', '=', ( 1, 3 ), None, None ),
        ( 't_done', None, None, 'h_done', None ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  def test_just_key_and_equal_with_trailing_white_space(self):
    t = self.call_lex_all(_test_keyval_lexer, 'ab= ',
      [
        ( 't_key', 'ab', ( 1, 1 ), None, None ),
        ( 't_key_value_delimiter', '=', ( 1, 3 ), None, None ),
        ( 't_space', '[SP]', ( 1, 4 ), None, None ),
        ( 't_done', None, None, 'h_done', None ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )
    
  def test_key_and_value_short(self):
    t = self.call_lex_all(_test_keyval_lexer, 'a=k',
      [
        ( 't_key', 'a', ( 1, 1 ), None, None ),
        ( 't_key_value_delimiter', '=', ( 1, 2 ), None, None ),
        ( 't_value', 'k', ( 1, 3 ), None, None ),
        ( 't_done', None, None, 'h_done', None ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  def test_key_and_value(self):
    t = self.call_lex_all(_test_keyval_lexer, 'fruit=kiwi',
      [
        ( 't_key', 'fruit', ( 1, 1 ), None, None ),
        ( 't_key_value_delimiter', '=', ( 1, 6 ), None, None ),
        ( 't_value', 'kiwi', ( 1, 7 ), None, None ),
        ( 't_done', None, None, 'h_done', None ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  def test_key_and_value_with_trailing_space(self):
    t = self.call_lex_all(_test_keyval_lexer, 'fruit=kiwi ',
      [
        ( 't_key', 'fruit', ( 1, 1 ), None, None ),
        ( 't_key_value_delimiter', '=', ( 1, 6 ), None, None ),
        ( 't_value', 'kiwi[SP]', ( 1, 7 ), None, None ),
        ( 't_done', None, None, 'h_done', None ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  def test_key_and_value_with_multiple_trailing_space(self):
    t = self.call_lex_all(_test_keyval_lexer, 'fruit=kiwi   ',
      [
        ( 't_key', 'fruit', ( 1, 1 ), None, None ),
        ( 't_key_value_delimiter', '=', ( 1, 6 ), None, None ),
        ( 't_value', 'kiwi[SP][SP][SP]', ( 1, 7 ), None, None ),
        ( 't_done', None, None, 'h_done', None ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )
    
  def test_one_space_before_key(self):
    t = self.call_lex_all(_test_keyval_lexer, ' k=v',
      [
        ( 't_space', '[SP]', ( 1, 1 ), None, None ),
        ( 't_key', 'k', ( 1, 2 ), None, None ),
        ( 't_key_value_delimiter', '=', ( 1, 3 ), None, None ),
        ( 't_value', 'v', ( 1, 4 ), None, None ),
        ( 't_done', None, None, 'h_done', None ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  def test_two_space_before_key(self):
    t = self.call_lex_all(_test_keyval_lexer, '  k=v',
      [
        ( 't_space', '[SP][SP]', ( 1, 1 ), None, None ),
        ( 't_key', 'k', ( 1, 3 ), None, None ),
        ( 't_key_value_delimiter', '=', ( 1, 4 ), None, None ),
        ( 't_value', 'v', ( 1, 5 ), None, None ),
        ( 't_done', None, None, 'h_done', None ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  def test_two_tab_before_key(self):
    t = self.call_lex_all(_test_keyval_lexer, '\t\tk=v',
      [
        ( 't_space', '[TAB][TAB]', ( 1, 1 ), None, None ),
        ( 't_key', 'k', ( 1, 3 ), None, None ),
        ( 't_key_value_delimiter', '=', ( 1, 4 ), None, None ),
        ( 't_value', 'v', ( 1, 5 ), None, None ),
        ( 't_done', None, None, 'h_done', None ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  def test_mixed_space_before_key(self):
    t = self.call_lex_all(_test_keyval_lexer, '\t k=v',
      [
        ( 't_space', '[TAB][SP]', ( 1, 1 ), None, None ),
        ( 't_key', 'k', ( 1, 3 ), None, None ),
        ( 't_key_value_delimiter', '=', ( 1, 4 ), None, None ),
        ( 't_value', 'v', ( 1, 5 ), None, None ),
        ( 't_done', None, None, 'h_done', None ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  def test_one_space_after_key(self):
    t = self.call_lex_all(_test_keyval_lexer, 'k =v',
      [
        ( 't_key', 'k', ( 1, 1 ), None, None ),
        ( 't_space', '[SP]', ( 1, 2 ), None, None ),
        ( 't_key_value_delimiter', '=', ( 1, 3 ), None, None ),
        ( 't_value', 'v', ( 1, 4 ), None, None ),
        ( 't_done', None, None, 'h_done', None ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )
    
  def test_two_space_after_key(self):
    t = self.call_lex_all(_test_keyval_lexer, 'k  =v',
      [
        ( 't_key', 'k', ( 1, 1 ), None, None ),
        ( 't_space', '[SP][SP]', ( 1, 2 ), None, None ),
        ( 't_key_value_delimiter', '=', ( 1, 4 ), None, None ),
        ( 't_value', 'v', ( 1, 5 ), None, None ),
        ( 't_done', None, None, 'h_done', None ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  def test_space_before_and_after_key(self):
    t = self.call_lex_all(_test_keyval_lexer, '\t k \t=v',
      [
        ( 't_space', '[TAB][SP]', ( 1, 1 ), None, None ),
        ( 't_key', 'k', ( 1, 3 ), None, None ),
        ( 't_space', '[SP][TAB]', ( 1, 4 ), None, None ),
        ( 't_key_value_delimiter', '=', ( 1, 6 ), None, None ),
        ( 't_value', 'v', ( 1, 7 ), None, None ),
        ( 't_done', None, None, 'h_done', None ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  def test_one_space_before_value(self):
    t = self.call_lex_all(_test_keyval_lexer, 'k= v',
      [
        ( 't_key', 'k', ( 1, 1 ), None, None ),
        ( 't_key_value_delimiter', '=', ( 1, 2 ), None, None ),
        ( 't_space', '[SP]', ( 1, 3 ), None, None ),
        ( 't_value', 'v', ( 1, 4 ), None, None ),
        ( 't_done', None, None, 'h_done', None ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  def test_multi_line_nl(self):
    t = self.call_lex_all(_test_keyval_lexer, '''\nfruit=kiwi\ncolor=green\n''', 
      [
        ( 't_line_break', '[NL]', ( 1, 1 ), 'h_line_break', None ),
        ( 't_key', 'fruit', ( 2, 1 ), None, None ),
        ( 't_key_value_delimiter', '=', ( 2, 6 ), None, None ),
        ( 't_value', 'kiwi', ( 2, 7 ), None, None ),
        ( 't_line_break', '[NL]', (  2, 11 ), 'h_line_break', None ),
        ( 't_key', 'color', ( 3, 1 ), None, None ),
        ( 't_key_value_delimiter', '=', ( 3, 6 ), None, None ),
        ( 't_value', 'green', ( 3, 7 ), None, None ),
        ( 't_line_break', '[NL]', (  3, 12 ), 'h_line_break', None ),
        ( 't_done', None, None, 'h_done', None ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  def test_multi_line_crlf(self):
    t = self.call_lex_all(_test_keyval_lexer, '''\r\nfruit=kiwi\r\ncolor=green\r\n''', 
      [
        ( 't_line_break', '[CR][NL]', ( 1, 1 ), 'h_line_break', None ),
        ( 't_key', 'fruit', ( 2, 1 ), None, None ),
        ( 't_key_value_delimiter', '=', ( 2, 6 ), None, None ),
        ( 't_value', 'kiwi', ( 2, 7 ), None, None ),
        ( 't_line_break', '[CR][NL]', (  2, 11 ), 'h_line_break', None ),
        ( 't_key', 'color', ( 3, 1 ), None, None ),
        ( 't_key_value_delimiter', '=', ( 3, 6 ), None, None ),
        ( 't_value', 'green', ( 3, 7 ), None, None ),
        ( 't_line_break', '[CR][NL]', (  3, 12 ), 'h_line_break', None ),
        ( 't_done', None, None, 'h_done', None ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  def test_error_no_key(self):
    with self.assertRaises(_test_keyval_lexer.e_unexpected_char) as ctx:
      self.call_lex_all(_test_keyval_lexer, '=', [])
    self.assertEqual( 'In state "s_start" unexpected character: "="', ctx.exception.message )
    
if __name__ == '__main__':
  unit_test.main()

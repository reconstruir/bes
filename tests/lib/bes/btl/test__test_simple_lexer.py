#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os

from bes.system.host import host
from bes.testing.unit_test import unit_test
from bes.testing.unit_test_function_skip import unit_test_function_skip

from bes.btl.btl_lexer_tester_mixin import btl_lexer_tester_mixin
from bes.btl.btl_lexer_token_deque import btl_lexer_token_deque
from bes.btl.btl_lexer_options import btl_lexer_options

from _test_simple_lexer import _test_simple_lexer

class test__test_simple_lexer(btl_lexer_tester_mixin, unit_test):

  def test_empty_string(self):
    t = self.call_lex_all(_test_simple_lexer, '',
      [
        ( 't_done', None, None, 'h_done', None ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  def test_just_key(self):
    t = self.call_lex_all(_test_simple_lexer, 'a',
      [
        ( 't_key', 'a', ( 1, 1 ), None, None ),
        ( 't_done', None, None, 'h_done', None ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )
    
  def test_just_key_and_equal(self):
    t = self.call_lex_all(_test_simple_lexer, 'ab=',
      [
        ( 't_key', 'ab', ( 1, 1 ), None, None ),
        ( 't_key_value_delimiter', '=', ( 1, 3 ), None, None ),
        ( 't_value', '', ( 1, 3 ), None, None ),
        ( 't_done', None, None, 'h_done', None ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  def test_key_and_value_short(self):
    t = self.call_lex_all(_test_simple_lexer, 'a=k',
      [
        ( 't_key', 'a', ( 1, 1 ), None, None ),
        ( 't_key_value_delimiter', '=', ( 1, 2 ), None, None ),
        ( 't_value', 'k', ( 1, 3 ), None, None ),
        ( 't_done', None, None, 'h_done', None ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  def test_key_and_value(self):
    t = self.call_lex_all(_test_simple_lexer, 'fruit=kiwi',
      [
        ( 't_key', 'fruit', ( 1, 1 ), None, None ),
        ( 't_key_value_delimiter', '=', ( 1, 6 ), None, None ),
        ( 't_value', 'kiwi', ( 1, 7 ), None, None ),
        ( 't_done', None, None, 'h_done', None ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  def test_caca_multi_line_nl(self):
    t = self.call_lex_all(_test_simple_lexer, '''\nfruit=kiwi\ncolor=green\n''',
      [
        ( 't_line_break', '[NL]', ( 1, 1 ), 'h_line_break', None ),
        ( 't_key', 'fruit', ( 2, 1 ), None, None ),
        ( 't_key_value_delimiter', '=', ( 2, 6 ), None, None ),
        ( 't_value', 'kiwi', ( 2, 7 ), None, None ),
        ( 't_line_break', '[NL]', ( 2, 11 ), 'h_line_break', None ),
        ( 't_key', 'color', ( 3, 1 ), None, None ),
        ( 't_key_value_delimiter', '=', ( 3, 6 ), None, None ),
        ( 't_value', 'green', ( 3, 7 ), None, None ),
        ( 't_line_break', '[NL]', ( 3, 12 ), 'h_line_break', None ),
        ( 't_done', None, None, 'h_done', None ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  def test_multi_line_crlf(self):
    t = self.call_lex_all(_test_simple_lexer, '''\r\nfruit=kiwi\r\ncolor=green\r\n''',
      [
        ( 't_line_break', '[CR][NL]', ( 1, 1 ), 'h_line_break', None ),
        ( 't_key', 'fruit', ( 2, 1 ), None, None ),
        ( 't_key_value_delimiter', '=', ( 2, 6 ), None, None ),
        ( 't_value', 'kiwi', ( 2, 7 ), None, None ),
        ( 't_line_break', '[CR][NL]', ( 2, 11 ), 'h_line_break', None ),
        ( 't_key', 'color', ( 3, 1 ), None, None ),
        ( 't_key_value_delimiter', '=', ( 3, 6 ), None, None ),
        ( 't_value', 'green', ( 3, 7 ), None, None ),
        ( 't_line_break', '[CR][NL]', ( 3, 12 ), 'h_line_break', None ),
        ( 't_done', None, None, 'h_done', None ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  @unit_test_function_skip.skip_if(not host.is_windows(), 'not windows')
  def test_multi_line_os_linesep_windows(self):
    t = self.call_lex_all(_test_simple_lexer, '''\r\nfruit=kiwi\r\ncolor=green\r\n''',
      [
        ( 't_line_break', os.linesep, ( 1, 1 ), 'h_line_break', None ),
        ( 't_key', 'fruit', ( 2, 1 ), None, None ),
        ( 't_key_value_delimiter', '=', ( 2, 6 ), None, None ),
        ( 't_value', 'kiwi', ( 2, 7 ), None, None ),
        ( 't_line_break', os.linesep, ( 2, 11 ), 'h_line_break', None ),
        ( 't_key', 'color', ( 3, 1 ), None, None ),
        ( 't_key_value_delimiter', '=', ( 3, 6 ), None, None ),
        ( 't_value', 'green', ( 3, 7 ), None, None ),
        ( 't_line_break', os.linesep, ( 3, 12 ), 'h_line_break', None ),
        ( 't_done', None, None, 'h_done', None ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  @unit_test_function_skip.skip_if(not host.is_unix(), 'not unix')
  def test_multi_line_os_linesep_unix(self):
    t = self.call_lex_all(_test_simple_lexer, '''\nfruit=kiwi\ncolor=green\n''',
      [
        ( 't_line_break', os.linesep, ( 1, 1 ), 'h_line_break', None ),
        ( 't_key', 'fruit', ( 2, 1 ), None, None ),
        ( 't_key_value_delimiter', '=', ( 2, 6 ), None, None ),
        ( 't_value', 'kiwi', ( 2, 7 ), None, None ),
        ( 't_line_break', os.linesep, ( 2, 11 ), 'h_line_break', None ),
        ( 't_key', 'color', ( 3, 1 ), None, None ),
        ( 't_key_value_delimiter', '=', ( 3, 6 ), None, None ),
        ( 't_value', 'green', ( 3, 7 ), None, None ),
        ( 't_line_break', os.linesep, ( 3, 12 ), 'h_line_break', None ),
        ( 't_done', None, None, 'h_done', None ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  def test_lex_all_multiple_sessions(self):
    l = _test_simple_lexer()
    expected_tokens = btl_lexer_token_deque([
      ( 't_key', 'a', ( 1, 1 ), None, None ),
      ( 't_key_value_delimiter', '=', ( 1, 2 ), None, None ),
      ( 't_value', 'k', ( 1, 3 ), None, None ),
      ( 't_done', None, None, 'h_done', None ),
    ])
    expected = '\n'.join([ token.to_debug_str() for token in expected_tokens ])
    actual_tokens = l.lex_all('a=k')
    actual = '\n'.join([ token.to_debug_str() for token in actual_tokens ])
    self.assertEqual( expected, actual )

    expected_tokens = btl_lexer_token_deque([
      ( 't_key', 'b', ( 1, 1 ), None, None ),
      ( 't_key_value_delimiter', '=', ( 1, 2 ), None, None ),
      ( 't_value', 'z', ( 1, 3 ), None, None ),
      ( 't_done', None, None, 'h_done', None ),
    ])
    expected = '\n'.join([ token.to_debug_str() for token in expected_tokens ])
    actual_tokens = l.lex_all('b=z')
    actual = '\n'.join([ token.to_debug_str() for token in actual_tokens ])
    self.assertEqual( expected, actual )

  def test_options_variables(self):
    variables = { 'v_key_value_delimiter': ':' }
    options = btl_lexer_options(variables = variables)
    t = self.call_lex_all(_test_simple_lexer, '''\nfruit:kiwi\ncolor:green\n''',
      [
        ( 't_line_break', '[NL]', ( 1, 1 ), 'h_line_break', None ),
        ( 't_key', 'fruit', ( 2, 1 ), None, None ),
        ( 't_key_value_delimiter', ':', ( 2, 6 ), None, None ),
        ( 't_value', 'kiwi', ( 2, 7 ), None, None ),
        ( 't_line_break', '[NL]', ( 2, 11 ), 'h_line_break', None ),
        ( 't_key', 'color', ( 3, 1 ), None, None ),
        ( 't_key_value_delimiter', ':', ( 3, 6 ), None, None ),
        ( 't_value', 'green', ( 3, 7 ), None, None ),
        ( 't_line_break', '[NL]', ( 3, 12 ), 'h_line_break', None ),
        ( 't_done', None, None, 'h_done', None ),
      ], options = options)
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )
    
if __name__ == '__main__':
  unit_test.main()

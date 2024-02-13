#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os

from collections import namedtuple

from bes.testing.unit_test import unit_test

from bes.btl.btl_lexer_tester_mixin import btl_lexer_tester_mixin
from bes.config.ini.bc_ini_lexer import bc_ini_lexer

class test_bc_ini_lexer(btl_lexer_tester_mixin, unit_test):

  def test_empty_string(self):
    t = self.call_lex_all(bc_ini_lexer, '',
      [
        ( 't_done', None, None, 'h_done', None ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  def test_just_key(self):
    t = self.call_lex_all(bc_ini_lexer, 'a',
      [
        ( 't_key', 'a', ( 1, 1 ), None, None ),
        ( 't_done', None, None, 'h_done', None ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )
    
  def test_just_key_and_equal(self):
    t = self.call_lex_all(bc_ini_lexer, 'ab=',
      [
        ( 't_key', 'ab', ( 1, 1 ), None, None ),
        ( 't_key_value_delimiter', '=', ( 1, 3 ), None, None ),
        ( 't_done', None, None, 'h_done', None ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  def test_just_key_and_equal_with_trailing_white_space(self):
    t = self.call_lex_all(bc_ini_lexer, 'ab= ',
      [
        ( 't_key', 'ab', ( 1, 1 ), None, None ),
        ( 't_key_value_delimiter', '=', ( 1, 3 ), None, None ),
        ( 't_space', '[SP]', ( 1, 4 ), None, None ),
        ( 't_done', None, None, 'h_done', None ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )
    
  def test_key_and_value_short(self):
    t = self.call_lex_all(bc_ini_lexer, 'a=k',
      [
        ( 't_key', 'a', ( 1, 1 ), None, None ),
        ( 't_key_value_delimiter', '=', ( 1, 2 ), None, None ),
        ( 't_value', 'k', ( 1, 3 ), None, None ),
        ( 't_done', None, None, 'h_done', None ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  def test_key_and_value(self):
    t = self.call_lex_all(bc_ini_lexer, 'fruit=kiwi',
      [
        ( 't_key', 'fruit', ( 1, 1 ), None, None ),
        ( 't_key_value_delimiter', '=', ( 1, 6 ), None, None ),
        ( 't_value', 'kiwi', ( 1, 7 ), None, None ),
        ( 't_done', None, None, 'h_done', None ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  def test_key_and_value_with_trailing_space(self):
    t = self.call_lex_all(bc_ini_lexer, 'fruit=kiwi ',
      [
        ( 't_key', 'fruit', ( 1, 1 ), None, None ),
        ( 't_key_value_delimiter', '=', ( 1, 6 ), None, None ),
        ( 't_value', 'kiwi ', ( 1, 7 ), None, None ),
        ( 't_done', None, None, 'h_done', None ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  def test_key_and_value_with_multiple_trailing_space(self):
    t = self.call_lex_all(bc_ini_lexer, 'fruit=kiwi   ',
      [
        ( 't_key', 'fruit', ( 1, 1 ), None, None ),
        ( 't_key_value_delimiter', '=', ( 1, 6 ), None, None ),
        ( 't_value', 'kiwi[SP][SP][SP]', ( 1, 7 ), None, None ),
        ( 't_done', None, None, 'h_done', None ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )
    
  def test_one_space_before_key(self):
    t = self.call_lex_all(bc_ini_lexer, ' k=v',
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
    t = self.call_lex_all(bc_ini_lexer, '  k=v',
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
    t = self.call_lex_all(bc_ini_lexer, '\t\tk=v',
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
    t = self.call_lex_all(bc_ini_lexer, '\t k=v',
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
    t = self.call_lex_all(bc_ini_lexer, 'k =v',
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
    t = self.call_lex_all(bc_ini_lexer, 'k  =v',
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
    t = self.call_lex_all(bc_ini_lexer, '\t k \t=v',
      [
        ( 't_space', '[TAB][SP]', ( 1, 1 ), None, None ),
        ( 't_key', 'k', ( 1, 3 ), None, None ),
        ( 't_space', ' [TAB]', ( 1, 4 ), None, None ),
        ( 't_key_value_delimiter', '=', ( 1, 6 ), None, None ),
        ( 't_value', 'v', ( 1, 7 ), None, None ),
        ( 't_done', None, None, 'h_done', None ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  def test_one_space_before_value(self):
    t = self.call_lex_all(bc_ini_lexer, 'k= v',
      [
        ( 't_key', 'k', ( 1, 1 ), None, None ),
        ( 't_key_value_delimiter', '=', ( 1, 2 ), None, None ),
        ( 't_space', '[SP]', ( 1, 3 ), None, None ),
        ( 't_value', 'v', ( 1, 4 ), None, None ),
        ( 't_done', None, None, 'h_done', None ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

    
  def test_multi_line(self):
    t = self.call_lex_all(bc_ini_lexer, '''\nfruit=kiwi\ncolor=green\n''', 
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
    t = self.call_lex_all(bc_ini_lexer, '''\r\nfruit=kiwi\r\ncolor=green\r\n;comment\r\n''', 
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
        ( 't_comment_begin', ';', ( 4, 1 ), None, None ),
        ( 't_comment', 'comment', ( 4, 2 ), None, None ),
        ( 't_line_break', '[CR][NL]', ( 4, 9 ), 'h_line_break', None ),
        ( 't_done', None, None, 'h_done', None ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  def test_multi_line_crlf_mixed_with_lf(self):
    t = self.call_lex_all(bc_ini_lexer, '''\r\nfruit=kiwi\ncolor=green\r\n;comment\r\n''', 
      [
        ( 't_line_break', '[CR][NL]', ( 1, 1 ), 'h_line_break', None ),
        ( 't_key', 'fruit', ( 2, 1 ), None, None ),
        ( 't_key_value_delimiter', '=', ( 2, 6 ), None, None ),
        ( 't_value', 'kiwi', ( 2, 7 ), None, None ),
        ( 't_line_break', '[NL]', (  2, 11 ), 'h_line_break', None ),
        ( 't_key', 'color', ( 3, 1 ), None, None ),
        ( 't_key_value_delimiter', '=', ( 3, 6 ), None, None ),
        ( 't_value', 'green', ( 3, 7 ), None, None ),
        ( 't_line_break', '[CR][NL]', (  3, 12 ), 'h_line_break', None ),
        ( 't_comment_begin', ';', ( 4, 1 ), None, None ),
        ( 't_comment', 'comment', ( 4, 2 ), None, None ),
        ( 't_line_break', '[CR][NL]', ( 4, 9 ), 'h_line_break', None ),
        ( 't_done', None, None, 'h_done', None ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )
    
  def test_section_one_section(self):
    t = self.call_lex_all(bc_ini_lexer, '''
[fruit.1]
name=kiwi
color=green
''', 
      [
        ( 't_line_break', '[NL]', ( 1, 1 ), 'h_line_break', None ),
        ( 't_section_name_begin', '[', ( 2, 1 ), None, None ),
        ( 't_section_name', 'fruit.1', ( 2, 2 ), None, None ),
        ( 't_section_name_end', ']', ( 2, 9 ), None, None ),
        ( 't_line_break', '[NL]', (  2, 10 ), 'h_line_break', None ),
        ( 't_key', 'name', ( 3, 1 ), None, None ),
        ( 't_key_value_delimiter', '=', ( 3, 5 ), None, None ),
        ( 't_value', 'kiwi', ( 3, 6 ), None, None ),
        ( 't_line_break', '[NL]', (  3, 10 ), 'h_line_break', None ),
        ( 't_key', 'color', ( 4, 1 ), None, None ),
        ( 't_key_value_delimiter', '=', ( 4, 6 ), None, None ),
        ( 't_value', 'green', ( 4, 7 ), None, None ),
        ( 't_line_break', '[NL]', (  4, 12 ), 'h_line_break', None ),
        ( 't_done', None, None, 'h_done', None ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  def test_section_with_comment(self):
    t = self.call_lex_all(bc_ini_lexer, '''
[fruit.1] ; this is fruit 1
name=kiwi
color=green
''', 
      [
        ( 't_line_break', '[NL]', ( 1, 1 ), 'h_line_break', None ),
        ( 't_section_name_begin', '[', ( 2, 1 ), None, None ),
        ( 't_section_name', 'fruit.1', ( 2, 2 ), None, None ),
        ( 't_section_name_end', ']', ( 2, 9 ), None, None ),
        ( 't_space', '[SP]', (  2, 10 ), None, None ),
        ( 't_comment_begin', ';', (  2, 11 ), None, None ),
        ( 't_comment', ' this is fruit 1', (  2, 12 ), None, None ),
        ( 't_line_break', '[NL]', (  2, 28 ), 'h_line_break', None ),
        ( 't_key', 'name', ( 3, 1 ), None, None ),
        ( 't_key_value_delimiter', '=', ( 3, 5 ), None, None ),
        ( 't_value', 'kiwi', ( 3, 6 ), None, None ),
        ( 't_line_break', '[NL]', (  3, 10 ), 'h_line_break', None ),
        ( 't_key', 'color', ( 4, 1 ), None, None ),
        ( 't_key_value_delimiter', '=', ( 4, 6 ), None, None ),
        ( 't_value', 'green', ( 4, 7 ), None, None ),
        ( 't_line_break', '[NL]', (  4, 12 ), 'h_line_break', None ),
        ( 't_done', None, None, 'h_done', None ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )
    
  def test_section_two_sections(self):
    t = self.call_lex_all(bc_ini_lexer, '''
[fruit.1]
name=kiwi
color=green

[fruit.2]
name=lemon
color=yellow
''', 
      [
        ( 't_line_break', '[NL]', ( 1, 1 ), 'h_line_break', None ),
        ( 't_section_name_begin', '[', ( 2, 1 ), None, None ),
        ( 't_section_name', 'fruit.1', ( 2, 2 ), None, None ),
        ( 't_section_name_end', ']', ( 2, 9 ), None, None ),
        ( 't_line_break', '[NL]', (  2, 10 ), 'h_line_break', None ),
        ( 't_key', 'name', ( 3, 1 ), None, None ),
        ( 't_key_value_delimiter', '=', ( 3, 5 ), None, None ),
        ( 't_value', 'kiwi', ( 3, 6 ), None, None ),
        ( 't_line_break', '[NL]', (  3, 10 ), 'h_line_break', None ),
        ( 't_key', 'color', ( 4, 1 ), None, None ),
        ( 't_key_value_delimiter', '=', ( 4, 6 ), None, None ),
        ( 't_value', 'green', ( 4, 7 ), None, None ),
        ( 't_line_break', '[NL]', (  4, 12 ), 'h_line_break', None ),
        ( 't_line_break', '[NL]', ( 5, 1 ), 'h_line_break', None ),
        ( 't_section_name_begin', '[', ( 6, 1 ), None, None ),
        ( 't_section_name', 'fruit.2', ( 6, 2 ), None, None ),
        ( 't_section_name_end', ']', ( 6, 9 ), None, None ),
        ( 't_line_break', '[NL]', (  6, 10 ), 'h_line_break', None ),
        ( 't_key', 'name', ( 7, 1 ), None, None ),
        ( 't_key_value_delimiter', '=', ( 7, 5 ), None, None ),
        ( 't_value', 'lemon', ( 7, 6 ), None, None ),
        ( 't_line_break', '[NL]', (  7, 11 ), 'h_line_break', None ),
        ( 't_key', 'color', ( 8, 1 ), None, None ),
        ( 't_key_value_delimiter', '=', ( 8, 6 ), None, None ),
        ( 't_value', 'yellow', ( 8, 7 ), None, None ),
        ( 't_line_break', '[NL]', (  8, 13 ), 'h_line_break', None ),
        ( 't_done', None, None, 'h_done', None ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  def test_comment_line(self):
    t = self.call_lex_all(bc_ini_lexer, '''
; fruit
name=kiwi
color=green
''', 
      [
        ( 't_line_break', '[NL]', ( 1, 1 ), 'h_line_break', None ),
        ( 't_comment_begin', ';', ( 2, 1 ), None, None ),
        ( 't_comment', ' fruit', ( 2, 2 ), None, None ),
        ( 't_line_break', '[NL]', ( 2, 8 ), 'h_line_break', None ),
        ( 't_key', 'name', ( 3, 1 ), None, None ),
        ( 't_key_value_delimiter', '=', ( 3, 5 ), None, None ),
        ( 't_value', 'kiwi', ( 3, 6 ), None, None ),
        ( 't_line_break', '[NL]', (  3, 10 ), 'h_line_break', None ),
        ( 't_key', 'color', ( 4, 1 ), None, None ),
        ( 't_key_value_delimiter', '=', ( 4, 6 ), None, None ),
        ( 't_value', 'green', ( 4, 7 ), None, None ),
        ( 't_line_break', '[NL]', (  4, 12 ), 'h_line_break', None ),
        ( 't_done', None, None, 'h_done', None ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

if __name__ == '__main__':
  unit_test.main()

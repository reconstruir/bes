#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os

from collections import namedtuple

from bes.testing.unit_test import unit_test

from bes.btl.btl_lexer_tester_mixin import btl_lexer_tester_mixin
from bes.config.ini.bc_ini_lexer import bc_ini_lexer

class test_bc_ini_lexer(btl_lexer_tester_mixin, unit_test):

  def test_empty_string(self):
    t = self.call_tokenize(bc_ini_lexer, '',
      [
        ( 't_done', None, None, 'h_done' ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  def test_just_key(self):
    t = self.call_tokenize(bc_ini_lexer, 'a',
      [
        ( 't_key', 'a', ( 1, 1 ), None ),
        ( 't_done', None, None, 'h_done' ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )
    
  def test_just_key_and_equal(self):
    t = self.call_tokenize(bc_ini_lexer, 'ab=',
      [
        ( 't_key', 'ab', ( 1, 1 ), None ),
        ( 't_key_value_delimiter', '=', ( 3, 1 ), None ),
        ( 't_done', None, None, 'h_done' ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  def test_just_key_and_equal_with_trailing_white_space(self):
    t = self.call_tokenize(bc_ini_lexer, 'ab= ',
      [
        ( 't_key', 'ab', ( 1, 1 ), None ),
        ( 't_key_value_delimiter', '=', ( 3, 1 ), None ),
        ( 't_space', '｢SP｣', ( 4, 1 ), None ),
        ( 't_done', None, None, 'h_done' ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )
    
  def test_key_and_value_short(self):
    t = self.call_tokenize(bc_ini_lexer, 'a=k',
      [
        ( 't_key', 'a', ( 1, 1 ), None ),
        ( 't_key_value_delimiter', '=', ( 2, 1 ), None ),
        ( 't_value', 'k', ( 3, 1 ), None ),
        ( 't_done', None, None, 'h_done' ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  def test_key_and_value(self):
    t = self.call_tokenize(bc_ini_lexer, 'fruit=kiwi',
      [
        ( 't_key', 'fruit', ( 1, 1 ), None ),
        ( 't_key_value_delimiter', '=', ( 6, 1 ), None ),
        ( 't_value', 'kiwi', ( 7, 1 ), None ),
        ( 't_done', None, None, 'h_done' ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  def test_key_and_value_with_trailing_space(self):
    t = self.call_tokenize(bc_ini_lexer, 'fruit=kiwi ',
      [
        ( 't_key', 'fruit', ( 1, 1 ), None ),
        ( 't_key_value_delimiter', '=', ( 6, 1 ), None ),
        ( 't_value', 'kiwi ', ( 7, 1 ), None ),
        ( 't_done', None, None, 'h_done' ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  def test_key_and_value_with_multiple_trailing_space(self):
    t = self.call_tokenize(bc_ini_lexer, 'fruit=kiwi   ',
      [
        ( 't_key', 'fruit', ( 1, 1 ), None ),
        ( 't_key_value_delimiter', '=', ( 6, 1 ), None ),
        ( 't_value', 'kiwi｢SP｣｢SP｣｢SP｣', ( 7, 1 ), None ),
        ( 't_done', None, None, 'h_done' ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )
    
  def test_one_space_before_key(self):
    t = self.call_tokenize(bc_ini_lexer, ' k=v',
      [
        ( 't_space', '｢SP｣', ( 1, 1 ), None ),
        ( 't_key', 'k', ( 2, 1 ), None ),
        ( 't_key_value_delimiter', '=', ( 3, 1 ), None ),
        ( 't_value', 'v', ( 4, 1 ), None ),
        ( 't_done', None, None, 'h_done' ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  def test_two_space_before_key(self):
    t = self.call_tokenize(bc_ini_lexer, '  k=v',
      [
        ( 't_space', '｢SP｣｢SP｣', ( 1, 1 ), None ),
        ( 't_key', 'k', ( 3, 1 ), None ),
        ( 't_key_value_delimiter', '=', ( 4, 1 ), None ),
        ( 't_value', 'v', ( 5, 1 ), None ),
        ( 't_done', None, None, 'h_done' ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  def test_two_tab_before_key(self):
    t = self.call_tokenize(bc_ini_lexer, '\t\tk=v',
      [
        ( 't_space', '｢TAB｣｢TAB｣', ( 1, 1 ), None ),
        ( 't_key', 'k', ( 3, 1 ), None ),
        ( 't_key_value_delimiter', '=', ( 4, 1 ), None ),
        ( 't_value', 'v', ( 5, 1 ), None ),
        ( 't_done', None, None, 'h_done' ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  def test_mixed_space_before_key(self):
    t = self.call_tokenize(bc_ini_lexer, '\t k=v',
      [
        ( 't_space', '｢TAB｣｢SP｣', ( 1, 1 ), None ),
        ( 't_key', 'k', ( 3, 1 ), None ),
        ( 't_key_value_delimiter', '=', ( 4, 1 ), None ),
        ( 't_value', 'v', ( 5, 1 ), None ),
        ( 't_done', None, None, 'h_done' ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  def test_one_space_after_key(self):
    t = self.call_tokenize(bc_ini_lexer, 'k =v',
      [
        ( 't_key', 'k', ( 1, 1 ), None ),
        ( 't_space', '｢SP｣', ( 2, 1 ), None ),
        ( 't_key_value_delimiter', '=', ( 3, 1 ), None ),
        ( 't_value', 'v', ( 4, 1 ), None ),
        ( 't_done', None, None, 'h_done' ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )
    
  def test_two_space_after_key(self):
    t = self.call_tokenize(bc_ini_lexer, 'k  =v',
      [
        ( 't_key', 'k', ( 1, 1 ), None ),
        ( 't_space', '｢SP｣｢SP｣', ( 2, 1 ), None ),
        ( 't_key_value_delimiter', '=', ( 4, 1 ), None ),
        ( 't_value', 'v', ( 5, 1 ), None ),
        ( 't_done', None, None, 'h_done' ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  def test_space_before_and_after_key(self):
    t = self.call_tokenize(bc_ini_lexer, '\t k \t=v',
      [
        ( 't_space', '｢TAB｣｢SP｣', ( 1, 1 ), None ),
        ( 't_key', 'k', ( 3, 1 ), None ),
        ( 't_space', ' ｢TAB｣', ( 4, 1 ), None ),
        ( 't_key_value_delimiter', '=', ( 6, 1 ), None ),
        ( 't_value', 'v', ( 7, 1 ), None ),
        ( 't_done', None, None, 'h_done' ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  def test_one_space_before_value(self):
    t = self.call_tokenize(bc_ini_lexer, 'k= v',
      [
        ( 't_key', 'k', ( 1, 1 ), None ),
        ( 't_key_value_delimiter', '=', ( 2, 1 ), None ),
        ( 't_space', '｢SP｣', ( 3, 1 ), None ),
        ( 't_value', 'v', ( 4, 1 ), None ),
        ( 't_done', None, None, 'h_done' ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

    
  def test_multi_line(self):
    t = self.call_tokenize(bc_ini_lexer, '''\nfruit=kiwi\ncolor=green\n''', 
      [
        ( 't_line_break', '｢NL｣', ( 1, 1 ), 'h_line_break' ),
        ( 't_key', 'fruit', ( 1, 2 ), None ),
        ( 't_key_value_delimiter', '=', ( 6, 2 ), None ),
        ( 't_value', 'kiwi', ( 7, 2 ), None ),
        ( 't_line_break', '｢NL｣', ( 11, 2 ), 'h_line_break' ),
        ( 't_key', 'color', ( 1, 3 ), None ),
        ( 't_key_value_delimiter', '=', ( 6, 3 ), None ),
        ( 't_value', 'green', ( 7, 3 ), None ),
        ( 't_line_break', '｢NL｣', ( 12, 3 ), 'h_line_break' ),
        ( 't_done', None, None, 'h_done' ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  def test_multi_line_crlf(self):
    t = self.call_tokenize(bc_ini_lexer, '''\r\nfruit=kiwi\r\ncolor=green\r\n;comment\r\n''', 
      [
        ( 't_line_break', '｢CR｣｢NL｣', ( 1, 1 ), 'h_line_break' ),
        ( 't_key', 'fruit', ( 1, 2 ), None ),
        ( 't_key_value_delimiter', '=', ( 6, 2 ), None ),
        ( 't_value', 'kiwi', ( 7, 2 ), None ),
        ( 't_line_break', '｢CR｣｢NL｣', ( 11, 2 ), 'h_line_break' ),
        ( 't_key', 'color', ( 1, 3 ), None ),
        ( 't_key_value_delimiter', '=', ( 6, 3 ), None ),
        ( 't_value', 'green', ( 7, 3 ), None ),
        ( 't_line_break', '｢CR｣｢NL｣', ( 12, 3 ), 'h_line_break' ),
        ( 't_comment_begin', ';', ( 1, 4 ), None ),
        ( 't_comment', 'comment', ( 2, 4 ), None ),
        ( 't_line_break', '｢CR｣｢NL｣', ( 9, 4 ), 'h_line_break' ),
        ( 't_done', None, None, 'h_done' ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  def test_multi_line_crlf_mixed_with_lf(self):
    t = self.call_tokenize(bc_ini_lexer, '''\r\nfruit=kiwi\ncolor=green\r\n;comment\r\n''', 
      [
        ( 't_line_break', '｢CR｣｢NL｣', ( 1, 1 ), 'h_line_break' ),
        ( 't_key', 'fruit', ( 1, 2 ), None ),
        ( 't_key_value_delimiter', '=', ( 6, 2 ), None ),
        ( 't_value', 'kiwi', ( 7, 2 ), None ),
        ( 't_line_break', '｢NL｣', ( 11, 2 ), 'h_line_break' ),
        ( 't_key', 'color', ( 1, 3 ), None ),
        ( 't_key_value_delimiter', '=', ( 6, 3 ), None ),
        ( 't_value', 'green', ( 7, 3 ), None ),
        ( 't_line_break', '｢CR｣｢NL｣', ( 12, 3 ), 'h_line_break' ),
        ( 't_comment_begin', ';', ( 1, 4 ), None ),
        ( 't_comment', 'comment', ( 2, 4 ), None ),
        ( 't_line_break', '｢CR｣｢NL｣', ( 9, 4 ), 'h_line_break' ),
        ( 't_done', None, None, 'h_done' ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )
    
  def test_section_one_section(self):
    t = self.call_tokenize(bc_ini_lexer, '''
[fruit.1]
name=kiwi
color=green
''', 
      [
        ( 't_line_break', '｢NL｣', ( 1, 1 ), 'h_line_break' ),
        ( 't_section_name_begin', '[', ( 1, 2 ), None ),
        ( 't_section_name', 'fruit.1', ( 2, 2 ), None ),
        ( 't_section_name_end', ']', ( 9, 2 ), None ),
        ( 't_line_break', '｢NL｣', ( 10, 2 ), 'h_line_break' ),
        ( 't_key', 'name', ( 1, 3 ), None ),
        ( 't_key_value_delimiter', '=', ( 5, 3 ), None ),
        ( 't_value', 'kiwi', ( 6, 3 ), None ),
        ( 't_line_break', '｢NL｣', ( 10, 3 ), 'h_line_break' ),
        ( 't_key', 'color', ( 1, 4 ), None ),
        ( 't_key_value_delimiter', '=', ( 6, 4 ), None ),
        ( 't_value', 'green', ( 7, 4 ), None ),
        ( 't_line_break', '｢NL｣', ( 12, 4 ), 'h_line_break' ),
        ( 't_done', None, None, 'h_done' ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  def test_section_with_comment(self):
    t = self.call_tokenize(bc_ini_lexer, '''
[fruit.1] ; this is fruit 1
name=kiwi
color=green
''', 
      [
        ( 't_line_break', '｢NL｣', ( 1, 1 ), 'h_line_break' ),
        ( 't_section_name_begin', '[', ( 1, 2 ), None ),
        ( 't_section_name', 'fruit.1', ( 2, 2 ), None ),
        ( 't_section_name_end', ']', ( 9, 2 ), None ),
        ( 't_space', '｢SP｣', ( 10, 2 ), None ),
        ( 't_comment_begin', ';', ( 11, 2 ), None ),
        ( 't_comment', ' this is fruit 1', ( 12, 2 ), None ),
        ( 't_line_break', '｢NL｣', ( 28, 2 ), 'h_line_break' ),
        ( 't_key', 'name', ( 1, 3 ), None ),
        ( 't_key_value_delimiter', '=', ( 5, 3 ), None ),
        ( 't_value', 'kiwi', ( 6, 3 ), None ),
        ( 't_line_break', '｢NL｣', ( 10, 3 ), 'h_line_break' ),
        ( 't_key', 'color', ( 1, 4 ), None ),
        ( 't_key_value_delimiter', '=', ( 6, 4 ), None ),
        ( 't_value', 'green', ( 7, 4 ), None ),
        ( 't_line_break', '｢NL｣', ( 12, 4 ), 'h_line_break' ),
        ( 't_done', None, None, 'h_done' ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )
    
  def test_section_two_sections(self):
    t = self.call_tokenize(bc_ini_lexer, '''
[fruit.1]
name=kiwi
color=green

[fruit.2]
name=lemon
color=yellow
''', 
      [
        ( 't_line_break', '｢NL｣', ( 1, 1 ), 'h_line_break' ),
        ( 't_section_name_begin', '[', ( 1, 2 ), None ),
        ( 't_section_name', 'fruit.1', ( 2, 2 ), None ),
        ( 't_section_name_end', ']', ( 9, 2 ), None ),
        ( 't_line_break', '｢NL｣', ( 10, 2 ), 'h_line_break' ),
        ( 't_key', 'name', ( 1, 3 ), None ),
        ( 't_key_value_delimiter', '=', ( 5, 3 ), None ),
        ( 't_value', 'kiwi', ( 6, 3 ), None ),
        ( 't_line_break', '｢NL｣', ( 10, 3 ), 'h_line_break' ),
        ( 't_key', 'color', ( 1, 4 ), None ),
        ( 't_key_value_delimiter', '=', ( 6, 4 ), None ),
        ( 't_value', 'green', ( 7, 4 ), None ),
        ( 't_line_break', '｢NL｣', ( 12, 4 ), 'h_line_break' ),
        ( 't_line_break', '｢NL｣', ( 1, 5 ), 'h_line_break' ),
        ( 't_section_name_begin', '[', ( 1, 6 ), None ),
        ( 't_section_name', 'fruit.2', ( 2, 6 ), None ),
        ( 't_section_name_end', ']', ( 9, 6 ), None ),
        ( 't_line_break', '｢NL｣', ( 10, 6 ), 'h_line_break' ),
        ( 't_key', 'name', ( 1, 7 ), None ),
        ( 't_key_value_delimiter', '=', ( 5, 7 ), None ),
        ( 't_value', 'lemon', ( 6, 7 ), None ),
        ( 't_line_break', '｢NL｣', ( 11, 7 ), 'h_line_break' ),
        ( 't_key', 'color', ( 1, 8 ), None ),
        ( 't_key_value_delimiter', '=', ( 6, 8 ), None ),
        ( 't_value', 'yellow', ( 7, 8 ), None ),
        ( 't_line_break', '｢NL｣', ( 13, 8 ), 'h_line_break' ),
        ( 't_done', None, None, 'h_done' ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  def test_comment_line(self):
    t = self.call_tokenize(bc_ini_lexer, '''
; fruit
name=kiwi
color=green
''', 
      [
        ( 't_line_break', '｢NL｣', ( 1, 1 ), 'h_line_break' ),
        ( 't_comment_begin', ';', ( 1, 2 ), None ),
        ( 't_comment', ' fruit', ( 2, 2 ), None ),
        ( 't_line_break', '｢NL｣', ( 8, 2 ), 'h_line_break' ),
        ( 't_key', 'name', ( 1, 3 ), None ),
        ( 't_key_value_delimiter', '=', ( 5, 3 ), None ),
        ( 't_value', 'kiwi', ( 6, 3 ), None ),
        ( 't_line_break', '｢NL｣', ( 10, 3 ), 'h_line_break' ),
        ( 't_key', 'color', ( 1, 4 ), None ),
        ( 't_key_value_delimiter', '=', ( 6, 4 ), None ),
        ( 't_value', 'green', ( 7, 4 ), None ),
        ( 't_line_break', '｢NL｣', ( 12, 4 ), 'h_line_break' ),
        ( 't_done', None, None, 'h_done' ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

if __name__ == '__main__':
  unit_test.main()

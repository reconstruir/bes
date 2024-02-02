#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.btl.btl_lexer_token_deque import btl_lexer_token_deque
from bes.btl.btl_lexer_token_lines import btl_lexer_token_lines
from bes.btl.btl_lexer_token import btl_lexer_token
from bes.btl.btl_error import btl_error
from bes.testing.unit_test import unit_test

from _test_lexer_desc_mixin import _test_lexer_desc_mixin

class test_btl_lexer_token_lines(_test_lexer_desc_mixin, unit_test):

  def test_to_source_string(self):
    tokens = btl_lexer_token_deque.parse_json(self._JSON_TEXT)
    lines = btl_lexer_token_lines(tokens)
    actual = lines.to_source_string()
    expected = '''
fruit=kiwi
color=green
'''
    self.assertMultiLineEqual( expected, actual )

  def test_modiy_value(self):
    tokens = btl_lexer_token_deque.parse_json(self._JSON_TEXT)
    lines = btl_lexer_token_lines(tokens)
    lines.modify_value(2, 't_value', 'watermelon')
    actual = lines.to_source_string()
    expected = '''
fruit=watermelon
color=green
'''
    self.assertMultiLineEqual( expected, actual )

  def test_insert_line_top(self):
    tokens = btl_lexer_token_deque.parse_json(self._JSON_TEXT)
    lines = btl_lexer_token_lines(tokens)
    new_tokens = btl_lexer_token_deque([
      ( 't_key', 'flavor', ( 1, -1 ), None ),
      ( 't_key_value_delimiter', '=', ( 7, -1 ), None ),
      ( 't_value', 'tart', ( 8, -1 ), None ),
      ( 't_line_break', '\n', ( 12, -1 ), 'h_line_break' ),
    ])
    lines.insert_line(1, new_tokens)
    actual = lines.to_source_string()
    expected = '''flavor=tart

fruit=kiwi
color=green
'''
    self.assertMultiLineEqual( expected, actual )

  def test_insert_line_middle(self):
    tokens = btl_lexer_token_deque.parse_json(self._JSON_TEXT)
    lines = btl_lexer_token_lines(tokens)
    new_tokens = btl_lexer_token_deque([
      ( 't_key', 'flavor', ( 1, -1 ), None ),
      ( 't_key_value_delimiter', '=', ( 7, -1 ), None ),
      ( 't_value', 'tart', ( 8, -1 ), None ),
      ( 't_line_break', '\n', ( 12, -1 ), 'h_line_break' ),
    ])
    lines.insert_line(3, new_tokens)
    actual = lines.to_source_string()
    expected = '''
fruit=kiwi
flavor=tart
color=green
'''
    self.assertMultiLineEqual( expected, actual )

  def test_insert_line_end(self):
    tokens = btl_lexer_token_deque.parse_json(self._JSON_TEXT)
    lines = btl_lexer_token_lines(tokens)
    new_tokens = btl_lexer_token_deque([
      ( 't_key', 'flavor', ( 1, -1 ), None ),
      ( 't_key_value_delimiter', '=', ( 7, -1 ), None ),
      ( 't_value', 'tart', ( 8, -1 ), None ),
      ( 't_line_break', '\n', ( 12, -1 ), 'h_line_break' ),
    ])
    lines.insert_line(5, new_tokens)
    actual = lines.to_source_string()
    expected = '''
fruit=kiwi
color=green
flavor=tart
'''
    self.assertMultiLineEqual( expected, actual )

  def test_insert_line_end_negative_one(self):
    tokens = btl_lexer_token_deque.parse_json(self._JSON_TEXT)
    lines = btl_lexer_token_lines(tokens)
    new_tokens = btl_lexer_token_deque([
      ( 't_key', 'flavor', ( 1, -1 ), None ),
      ( 't_key_value_delimiter', '=', ( 7, -1 ), None ),
      ( 't_value', 'tart', ( 8, -1 ), None ),
      ( 't_line_break', '\n', ( 12, -1 ), 'h_line_break' ),
    ])
    lines.insert_line(-1, new_tokens)
    actual = lines.to_source_string()
    expected = '''
fruit=kiwi
color=green
flavor=tart
'''
    self.assertMultiLineEqual( expected, actual )

  def test_to_json(self):
    tokens = btl_lexer_token_deque.parse_json(self._JSON_TEXT)
    lines = btl_lexer_token_lines(tokens)
    self.assert_json_equal( '''
[
  {
    "line_number": 1,
    "tokens": [
      {
        "name": "t_line_break",
        "value": "\\n",
        "position": "1,1",
        "type_hint": "h_line_break"
      }
    ]
  },
  {
    "line_number": 2,
    "tokens": [
      {
        "name": "t_key",
        "value": "fruit",
        "position": "1,2",
        "type_hint": null
      },
      {
        "name": "t_key_value_delimiter",
        "value": "=",
        "position": "6,2",
        "type_hint": null
      },
      {
        "name": "t_value",
        "value": "kiwi",
        "position": "7,2",
        "type_hint": null
      },
      {
        "name": "t_line_break",
        "value": "\\n",
        "position": "11,2",
        "type_hint": "h_line_break"
      }
    ]
  },
  {
    "line_number": 3,
    "tokens": [
      {
        "name": "t_key",
        "value": "color",
        "position": "1,3",
        "type_hint": null
      },
      {
        "name": "t_key_value_delimiter",
        "value": "=",
        "position": "6,3",
        "type_hint": null
      },
      {
        "name": "t_value",
        "value": "green",
        "position": "7,3",
        "type_hint": null
      },
      {
        "name": "t_line_break",
        "value": "\\n",
        "position": "12,3",
        "type_hint": "h_line_break"
      }
    ]
  }
]
''', lines.to_json() )
    
  _JSON_TEXT = '''
[
  {
    "name": "t_line_break", 
    "value": "\\n", 
    "position": "1,1", 
    "type_hint": "h_line_break"
  }, 
  {
    "name": "t_key", 
    "value": "fruit", 
    "position": "1,2", 
    "type_hint": null
  }, 
  {
    "name": "t_key_value_delimiter", 
    "value": "=", 
    "position": "6,2", 
    "type_hint": null
  }, 
  {
    "name": "t_value", 
    "value": "kiwi", 
    "position": "7,2", 
    "type_hint": null
  }, 
  {
    "name": "t_line_break", 
    "value": "\\n", 
    "position": "11,2", 
    "type_hint": "h_line_break"
  }, 
  {
    "name": "t_key", 
    "value": "color", 
    "position": "1,3", 
    "type_hint": null
  }, 
  {
    "name": "t_key_value_delimiter", 
    "value": "=", 
    "position": "6,3", 
    "type_hint": null
  }, 
  {
    "name": "t_value", 
    "value": "green", 
    "position": "7,3", 
    "type_hint": null
  }, 
  {
    "name": "t_line_break", 
    "value": "\\n", 
    "position": "12,3", 
    "type_hint": "h_line_break"
  }, 
  {
    "name": "t_done", 
    "value": null, 
    "position": "", 
    "type_hint": "h_done"
  }
]
'''
    
if __name__ == '__main__':
  unit_test.main()

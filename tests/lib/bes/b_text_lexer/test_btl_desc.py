#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.b_text_lexer.btl_desc import btl_desc
from bes.b_text_lexer.btl_desc_char import btl_desc_char
from bes.b_text_lexer.btl_desc_char_map import btl_desc_char_map
from bes.b_text_lexer.btl_error import btl_error
from bes.testing.unit_test import unit_test

from keyval_desc_mixin import keyval_desc_mixin

class test_btl_desc(keyval_desc_mixin, unit_test):

  def test_parse_text_to_json(self):
    self.assert_string_equal_fuzzy( r'''
{
  "header": {
    "name": "keyval", 
    "description": "A Key Value pair lexer", 
    "version": "1.0", 
    "start_state": "s_expecting_key", 
    "end_state": "s_done"
  }, 
  "tokens": [
    "t_done", 
    "t_expecting_key", 
    "t_key", 
    "t_line_break", 
    "t_space", 
    "t_value"
  ], 
  "errors": [
    {
      "name": "unexpected_char", 
      "message": "In state {state} unexpected character {char} instead of key"
    }
  ], 
  "char_map": {
    "c_keyval_key_first": {
      "name": "c_keyval_key_first", 
      "chars": [
        65, 
        66, 
        67, 
        68, 
        69, 
        70, 
        71, 
        72, 
        73, 
        74, 
        75, 
        76, 
        77, 
        78, 
        79, 
        80, 
        81, 
        82, 
        83, 
        84, 
        85, 
        86, 
        87, 
        88, 
        89, 
        90, 
        95, 
        97, 
        98, 
        99, 
        100, 
        101, 
        102, 
        103, 
        104, 
        105, 
        106, 
        107, 
        108, 
        109, 
        110, 
        111, 
        112, 
        113, 
        114, 
        115, 
        116, 
        117, 
        118, 
        119, 
        120, 
        121, 
        122
      ]
    }, 
    "c_keyval_key": {
      "name": "c_keyval_key", 
      "chars": [
        48, 
        49, 
        50, 
        51, 
        52, 
        53, 
        54, 
        55, 
        56, 
        57, 
        65, 
        66, 
        67, 
        68, 
        69, 
        70, 
        71, 
        72, 
        73, 
        74, 
        75, 
        76, 
        77, 
        78, 
        79, 
        80, 
        81, 
        82, 
        83, 
        84, 
        85, 
        86, 
        87, 
        88, 
        89, 
        90, 
        95, 
        97, 
        98, 
        99, 
        100, 
        101, 
        102, 
        103, 
        104, 
        105, 
        106, 
        107, 
        108, 
        109, 
        110, 
        111, 
        112, 
        113, 
        114, 
        115, 
        116, 
        117, 
        118, 
        119, 
        120, 
        121, 
        122
      ]
    }
  }, 
  "states": [
    {
      "name": "s_expecting_key", 
      "transitions": [
        {
          "to_state": "s_done", 
          "char_name": "c_eos", 
          "commands": [
            {
              "name": "yield", 
              "arg": "t_done"
            }
          ]
        }, 
        {
          "to_state": "s_expecting_key", 
          "char_name": "c_new_line", 
          "commands": [
            {
              "name": "yield", 
              "arg": "t_line_break"
            }
          ]
        }, 
        {
          "to_state": "s_expecting_key", 
          "char_name": "c_white_space", 
          "commands": [
            {
              "name": "yield", 
              "arg": "t_space"
            }
          ]
        }, 
        {
          "to_state": "s_key", 
          "char_name": "c_keyval_key_first", 
          "commands": [
            {
              "name": "buffer", 
              "arg": "write" 
            }
          ]
        }, 
        {
          "to_state": "s_expecting_key_error", 
          "char_name": "default", 
          "commands": [
            {
              "name": "raise", 
              "arg": "unexpected_char"
            }
          ]
        }
      ]
    }, 
    {
      "name": "s_key", 
      "transitions": [
        {
          "to_state": "s_key", 
          "char_name": "c_keyval_key", 
          "commands": [
            {
              "name": "buffer", 
              "arg": "write" 
            }
          ]
        }, 
        {
          "to_state": "s_value", 
          "char_name": "c_equal", 
          "commands": [
            {
              "name": "yield", 
              "arg": "t_key"
            }
          ]
        }, 
        {
          "to_state": "s_done", 
          "char_name": "c_eos", 
          "commands": [
            {
              "name": "yield", 
              "arg": "t_done"
            }
          ]
        }
      ]
    }, 
    {
      "name": "s_value", 
      "transitions": [
        {
          "to_state": "s_expecting_key", 
          "char_name": "c_new_line", 
          "commands": [
            {
              "name": "yield", 
              "arg": "t_line_break"
            }, 
            {
              "name": "yield", 
              "arg": "t_value"
            }
          ]
        }, 
        {
          "to_state": "s_done", 
          "char_name": "c_eos", 
          "commands": [
            {
              "name": "yield", 
              "arg": "t_done"
            }
          ]
        }, 
        {
          "to_state": "s_value", 
          "char_name": "default", 
          "commands": [
            {
              "name": "buffer", 
              "arg": "write" 
            }
          ]
        }
      ]
    }, 
    {
      "name": "s_done", 
      "transitions": []
    }
  ]
}
''', btl_desc.parse_text(self._keyval_desc_text).to_json() )

  def test_to_mermaid_diagram(self):
    #print(btl_desc.parse_text(self._keyval_desc_text).to_mermaid_diagram())
    #return
    self.assertEqual( '''\
stateDiagram-v2
  direction LR

  %% s_expecting_key state
  [*] --> s_expecting_key
  s_expecting_key --> s_done: c_eos
  s_expecting_key --> s_expecting_key: c_new_line
  s_expecting_key --> s_expecting_key: c_white_space
  s_expecting_key --> s_key: c_keyval_key_first
  s_expecting_key --> s_expecting_key_error: default

  %% s_key state
  s_key --> s_key: c_keyval_key
  s_key --> s_value: c_equal
  s_key --> s_done: c_eos

  %% s_value state
  s_value --> s_expecting_key: c_new_line
  s_value --> s_done: c_eos
  s_value --> s_value: default

  %% s_done state
  s_done --> [*]
''', btl_desc.parse_text(self._keyval_desc_text).to_mermaid_diagram() )
    
if __name__ == '__main__':
  unit_test.main()

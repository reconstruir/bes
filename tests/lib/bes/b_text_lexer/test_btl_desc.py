#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.b_text_lexer.btl_desc import btl_desc
from bes.b_text_lexer.btl_desc_char import btl_desc_char
from bes.b_text_lexer.btl_desc_char_map import btl_desc_char_map
from bes.b_text_lexer.btl_error import btl_error
from bes.testing.unit_test import unit_test
from bes.property.cached_property import cached_property
from bes.fs.file_util import file_util

from keyval_desc_mixin import keyval_desc_mixin

class test_btl_desc(keyval_desc_mixin, unit_test):

  def test_parse_text(self):
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
          "char": "c_eos: s_done", 
          "commands": [
            {
              "name": "yield", 
              "arg": "t_done"
            }
          ]
        }, 
        {
          "char": "c_new_line: s_expecting_key", 
          "commands": [
            {
              "name": "yield", 
              "arg": "t_line_break"
            }
          ]
        }, 
        {
          "char": "c_white_space: s_expecting_key", 
          "commands": [
            {
              "name": "yield", 
              "arg": "t_space"
            }
          ]
        }, 
        {
          "char": "c_keyval_key_first: s_key", 
          "commands": [
            {
              "name": "buffer", 
              "arg": null
            }
          ]
        }, 
        {
          "char": "default: s_expecting_key_error", 
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
          "char": "c_keyval_key: s_key", 
          "commands": [
            {
              "name": "buffer", 
              "arg": null
            }
          ]
        }, 
        {
          "char": "c_equal: s_value", 
          "commands": [
            {
              "name": "yield", 
              "arg": "t_key"
            }
          ]
        }, 
        {
          "char": "c_eos: s_done", 
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
          "char": "c_new_line: s_expecting_key", 
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
          "char": "c_eos: s_done", 
          "commands": [
            {
              "name": "yield", 
              "arg": "t_done"
            }
          ]
        }, 
        {
          "char": "default: s_value", 
          "commands": [
            {
              "name": "buffer", 
              "arg": null
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
    
if __name__ == '__main__':
  unit_test.main()

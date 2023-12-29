 #!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.fs.file_util import file_util
from bes.b_text_lexer.btl_desc import btl_desc
from bes.b_text_lexer.btl_desc_char import btl_desc_char
from bes.b_text_lexer.btl_desc_char_map import btl_desc_char_map
from bes.b_text_lexer.btl_desc_char_map import btl_desc_char_map
from bes.b_text_lexer.btl_desc_state import btl_desc_state
from bes.b_text_lexer.btl_desc_state_command import btl_desc_state_command
from bes.b_text_lexer.btl_desc_state_transition import btl_desc_state_transition
from bes.b_text_lexer.btl_error import btl_error
from bes.testing.unit_test import unit_test

from keyval_desc_mixin import keyval_desc_mixin

class test_btl_desc(keyval_desc_mixin, unit_test):

  def test_parse_text_to_json(self):
    #print(btl_desc.parse_text(self._keyval_desc_text).to_json())
    #return
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
          "char_name": "c_nl", 
          "commands": [
            {
              "name": "yield", 
              "arg": "t_line_break"
            }
          ]
        }, 
        {
          "to_state": "s_expecting_key", 
          "char_name": "c_ws", 
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
      ], 
      "is_end_state": false
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
      ], 
      "is_end_state": false
    }, 
    {
      "name": "s_value", 
      "transitions": [
        {
          "to_state": "s_expecting_key", 
          "char_name": "c_nl", 
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
      ], 
      "is_end_state": false
    }, 
    {
      "name": "s_done", 
      "transitions": [], 
      "is_end_state": false
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
  s_expecting_key --> s_expecting_key: c_nl
  s_expecting_key --> s_expecting_key: c_ws
  s_expecting_key --> s_key: c_keyval_key_first
  s_expecting_key --> s_expecting_key_error: default

  %% s_key state
  s_key --> s_key: c_keyval_key
  s_key --> s_value: c_equal
  s_key --> s_done: c_eos

  %% s_value state
  s_value --> s_expecting_key: c_nl
  s_value --> s_done: c_eos
  s_value --> s_value: default

  %% s_done state
  s_done --> [*]
''', btl_desc.parse_text(self._keyval_desc_text).to_mermaid_diagram() )

  def test_generate_code(self):
    desc = btl_desc.parse_text(self._keyval_desc_text)
    self.assert_code_equal(
      self._EXPECTED_CODE,
      self.call_buf_func(desc, 'generate_code', '_fruit', 'kiwi')
    )

  def test_write_code(self):
    tmp = self.make_temp_file(suffix = '.py')
    desc = btl_desc.parse_text(self._keyval_desc_text)
    desc.write_code(tmp, '_fruit', 'kiwi')

    self.assert_code_equal( self._EXPECTED_CODE, file_util.read(tmp, codec = 'utf-8') )
    
  _EXPECTED_CODE = '''
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.b_text_lexer.btl_lexer_base import btl_lexer_base
from bes.b_text_lexer.btl_lexer_state_base import btl_lexer_state_base


class _fruit_kiwi_lexer_token(object):

  def __init__(self, lexer):
    check.check_text_lexer(lexer)
  
    self._lexer = lexer
  
  T_DONE = 't_done'
  def make_t_done(self, value, position):
    return lexer_token(self.T_DONE, value, self._lexer.position)
  
  T_EXPECTING_KEY = 't_expecting_key'
  def make_t_expecting_key(self, value, position):
    return lexer_token(self.T_EXPECTING_KEY, value, self._lexer.position)
  
  T_KEY = 't_key'
  def make_t_key(self, value, position):
    return lexer_token(self.T_KEY, value, self._lexer.position)
  
  T_LINE_BREAK = 't_line_break'
  def make_t_line_break(self, value, position):
    return lexer_token(self.T_LINE_BREAK, value, self._lexer.position)
  
  T_SPACE = 't_space'
  def make_t_space(self, value, position):
    return lexer_token(self.T_SPACE, value, self._lexer.position)
  
  T_VALUE = 't_value'
  def make_t_value(self, value, position):
    return lexer_token(self.T_VALUE, value, self._lexer.position)

class _fruit_kiwi_lexer_state_s_expecting_key(btl_lexer_state_base):
  def __init__(self, lexer):
    super().__init__(lexer)

  def handle_char(self, c):
    self.log_handle_char(c)

    new_state = None
    tokens = []

    if c in {0}:
      new_state = s_done
      tokens.append(self.make_token(t_done, self.buffer_value(), self.position)
    elif c in {10}:
      new_state = s_expecting_key
      tokens.append(self.make_token(t_line_break, self.buffer_value(), self.position)
    elif c in {32, 9}:
      new_state = s_expecting_key
      tokens.append(self.make_token(t_space, self.buffer_value(), self.position)
    elif c in {65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 95, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122}:
      new_state = s_key
      self.lexer.buffer_write(c)
    else:
      new_state = s_expecting_key_error
    
    self.lexer.change_state(new_state, c)
    return tokens

class _fruit_kiwi_lexer_state_s_key(btl_lexer_state_base):
  def __init__(self, lexer):
    super().__init__(lexer)

  def handle_char(self, c):
    self.log_handle_char(c)

    new_state = None
    tokens = []

    if c in {48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 95, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122}:
      new_state = s_key
      self.lexer.buffer_write(c)
    elif c in {61}:
      new_state = s_value
      tokens.append(self.make_token(t_key, self.buffer_value(), self.position)
    elif c in {0}:
      new_state = s_done
      tokens.append(self.make_token(t_done, self.buffer_value(), self.position)
    
    self.lexer.change_state(new_state, c)
    return tokens

class _fruit_kiwi_lexer_state_s_value(btl_lexer_state_base):
  def __init__(self, lexer):
    super().__init__(lexer)

  def handle_char(self, c):
    self.log_handle_char(c)

    new_state = None
    tokens = []

    if c in {10}:
      new_state = s_expecting_key
      tokens.append(self.make_token(t_line_break, self.buffer_value(), self.position)
      tokens.append(self.make_token(t_value, self.buffer_value(), self.position)
    elif c in {0}:
      new_state = s_done
      tokens.append(self.make_token(t_done, self.buffer_value(), self.position)
    else:
      new_state = s_value
      self.lexer.buffer_write(c)
    
    self.lexer.change_state(new_state, c)
    return tokens

class _fruit_kiwi_lexer_state_s_done(btl_lexer_state_base):
  def __init__(self, lexer):
    super().__init__(lexer)

  def handle_char(self, c):
    self.log_handle_char(c)

    new_state = None
    tokens = []

    
    self.lexer.change_state(new_state, c)
    return tokens

class _fruit_kiwi_lexer_base(text_lexer_base):

  def __init__(self, kiwi, source = None):
    super().__init__(log_tag, source = source)

    self.token = _fruit_kiwi_lexer_token(self)
    self.char = text_lexer_char
    
    self._states = {
      's_expecting_key': _fruit_kiwi_lexer_state_s_expecting_key(self),
      's_key': _fruit_kiwi_lexer_state_s_key(self),
      's_value': _fruit_kiwi_lexer_state_s_value(self),
      's_done': _fruit_kiwi_lexer_state_s_done(self),
    }
'''
  
if __name__ == '__main__':
  unit_test.main()

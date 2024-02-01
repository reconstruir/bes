#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os

from bes.fs.file_util import file_util
from bes.property.cached_class_property import cached_class_property
from bes.system.check import check
from bes.system.execute import execute
from bes.testing.unit_test import unit_test
from bes.text.text_line_parser import text_line_parser

from bes.btl.btl_lexer_desc import btl_lexer_desc
from bes.btl.btl_lexer_desc_char import btl_lexer_desc_char
from bes.btl.btl_lexer_desc_char_map import btl_lexer_desc_char_map
from bes.btl.btl_lexer_desc_char_map import btl_lexer_desc_char_map
from bes.btl.btl_lexer_desc_state import btl_lexer_desc_state
from bes.btl.btl_lexer_desc_state_command import btl_lexer_desc_state_command
from bes.btl.btl_lexer_desc_state_transition import btl_lexer_desc_state_transition
from bes.btl.btl_error import btl_error

from _test_lexer_desc_mixin import _test_lexer_desc_mixin

class test_btl_lexer_desc(_test_lexer_desc_mixin, unit_test):

  def test_parse_text_to_json(self):
    #print(btl_lexer_desc.parse_text(self._keyval1_desc_text).to_json())
    #return
    self.assert_string_equal_fuzzy(
      self._DESC_JSON,
      btl_lexer_desc.parse_text(self._keyval1_desc_text).to_json()
    )

  def test_to_mermaid_diagram(self):
    #print(btl_lexer_desc.parse_text(self._keyval1_desc_text).to_mermaid_diagram())
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

  %% s_expecting_key_error state
  s_expecting_key_error --> s_done: default

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
''', btl_lexer_desc.parse_text(self._keyval1_desc_text).to_mermaid_diagram() )

  def test_generate_code(self):
    desc = btl_lexer_desc.parse_text(self._keyval1_desc_text)
    actual = self.call_buf_func(desc, 'generate_code', '_fruit', 'kiwi_lexer')
    #print(actual)
    #return
    self.assert_code_equal( self._EXPECTED_CODE, actual )

  def test_write_code(self):
    tmp = self.make_temp_file(suffix = '.py')
    desc = btl_lexer_desc.parse_text(self._keyval1_desc_text)
    desc.write_code(tmp, '_fruit', 'kiwi_lexer')

    self.assert_code_equal( self._EXPECTED_CODE, file_util.read(tmp, codec = 'utf-8') )

  @classmethod
  def _add_line_numbers(clazz, code):
    p = text_line_parser(code)
    p.add_line_numbers()
    return str(p)
      
  def test_use_code(self):
    desc = btl_lexer_desc.parse_text(self._keyval1_desc_text)
    lexer_code = self.call_buf_func(desc, 'generate_code', '_fruit', 'kiwi_lexer')
    use_code = '''
import unittest

class _test_use_code_unit_test(unittest.TestCase):

  def test_use_code_generated(self):
    l = _fruit_kiwi_lexer()

    text = f"""
fruit=kiwi
color=green
taste=sour
"""
    self.assertEqual( 's_expecting_key', l.desc.header.start_state )
    self.assertEqual( 's_done', l.desc.header.end_state )
    self.assertEqual( 's_expecting_key', l._states['s_expecting_key'].name )

    tokens = l.run(text)
    def _hack_token(token_):
      if token_.name == 't_line_break':
        return token_.clone(mutations = { 'value': '\\n' })
      return token_
    hacked_tokens = [ _hack_token(token) for token in tokens ]
    expected = [
      '0: t_line_break:\\n:1,1:h_line_break',
      '1: t_key:fruit:1,2',
      '2: t_equal:=:6,2',
      '3: t_value:kiwi:7,2',
      '4: t_line_break:\\n:11,2:h_line_break',
      '5: t_key:color:1,3',
      '6: t_equal:=:6,3',
      '7: t_value:green:7,3',
      '8: t_line_break:\\n:12,3:h_line_break',
      '9: t_key:taste:1,4',
      '10: t_equal:=:6,4',
      '11: t_value:sour:7,4',
      '12: t_line_break:\\n:11,4:h_line_break',
      '13: t_done:::h_done',
    ]
    actual = [ f'{i}: {str(token)}' for i, token in enumerate(hacked_tokens) ]
    self.assertEqual( expected, actual )

if __name__ == '__main__':
  unittest.main()
'''
    code = lexer_code + use_code
    tmp = self.make_temp_file(suffix = '.py', content = code, perm = 0o0755)
    rv = execute.execute(tmp, stderr_to_stdout = True, raise_error = False)
    if rv.exit_code != 0:
      code_with_line_numbers = self._add_line_numbers(code)
      print(code_with_line_numbers, flush = True)
    if self.DEBUG or rv.exit_code != 0:
      print(rv.stdout, flush = True)
    self.assertEqual( 0, rv.exit_code )

  def test_to_json(self):
    desc = btl_lexer_desc.parse_text(self._keyval1_desc_text)
    actual = desc.to_json()
    #print(actual)
    #return
    self.assert_json_equal( self._DESC_JSON, actual )

  @cached_class_property
  def _EXPECTED_CODE(clazz):
    return clazz._EXPECTED_CODE_TEMPLATE.replace('@@@_DESC_TEXT@@@', clazz._keyval1_desc_text)
    
  _EXPECTED_CODE_TEMPLATE = '''
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.btl.btl_lexer_base import btl_lexer_base
from bes.btl.btl_lexer_state_base import btl_lexer_state_base
from bes.btl.btl_lexer_token import btl_lexer_token
from bes.system.check import check

class _fruit_kiwi_lexer(btl_lexer_base):

  class _token:

    T_DONE = 't_done'
    T_EQUAL = 't_equal'
    T_KEY = 't_key'
    T_LINE_BREAK = 't_line_break'
    T_SPACE = 't_space'
    T_VALUE = 't_value'
  
  class _state_s_expecting_key(btl_lexer_state_base):
    def __init__(self, lexer, log_tag):
      name = 's_expecting_key'
      super().__init__(lexer, name, log_tag)
  
    def handle_char(self, c):
      self.log_handle_char(c)
  
      new_state = None
      tokens = []
  
      if self.char_in(c, 'c_eos'):
        new_state = 's_done'
        tokens.append(self.make_token('t_done', args = {}))
      elif self.char_in(c, 'c_nl'):
        new_state = 's_expecting_key'
        self.buffer_write(c)
        tokens.append(self.make_token('t_line_break', args = {}))
        self.buffer_reset()
      elif self.char_in(c, 'c_ws'):
        new_state = 's_expecting_key'
        tokens.append(self.make_token('t_space', args = {}))
      elif self.char_in(c, 'c_keyval_key_first'):
        new_state = 's_key'
        self.buffer_write(c)
      else:
        new_state = 's_expecting_key_error'
      
      self.lexer.change_state(new_state, c)
      return tokens
  
  class _state_s_expecting_key_error(btl_lexer_state_base):
    def __init__(self, lexer, log_tag):
      name = 's_expecting_key_error'
      super().__init__(lexer, name, log_tag)
  
    def handle_char(self, c):
      self.log_handle_char(c)
  
      new_state = None
      tokens = []
  
      if True:
        new_state = 's_done'
      
      self.lexer.change_state(new_state, c)
      return tokens
  
  class _state_s_key(btl_lexer_state_base):
    def __init__(self, lexer, log_tag):
      name = 's_key'
      super().__init__(lexer, name, log_tag)
  
    def handle_char(self, c):
      self.log_handle_char(c)
  
      new_state = None
      tokens = []
  
      if self.char_in(c, 'c_keyval_key'):
        new_state = 's_key'
        self.buffer_write(c)
      elif self.char_in(c, 'c_equal'):
        new_state = 's_value'
        tokens.append(self.make_token('t_key', args = {}))
        self.buffer_reset()
        self.buffer_write(c)
        tokens.append(self.make_token('t_equal', args = {}))
        self.buffer_reset()
      elif self.char_in(c, 'c_eos'):
        new_state = 's_done'
        tokens.append(self.make_token('t_key', args = {}))
        self.buffer_reset()
        tokens.append(self.make_token('t_done', args = {}))
      
      self.lexer.change_state(new_state, c)
      return tokens
  
  class _state_s_value(btl_lexer_state_base):
    def __init__(self, lexer, log_tag):
      name = 's_value'
      super().__init__(lexer, name, log_tag)
  
    def handle_char(self, c):
      self.log_handle_char(c)
  
      new_state = None
      tokens = []
  
      if self.char_in(c, 'c_nl'):
        new_state = 's_expecting_key'
        tokens.append(self.make_token('t_value', args = {}))
        self.buffer_reset()
        self.buffer_write(c)
        tokens.append(self.make_token('t_line_break', args = {}))
        self.buffer_reset()
      elif self.char_in(c, 'c_eos'):
        new_state = 's_done'
        tokens.append(self.make_token('t_value', args = {}))
        self.buffer_reset()
        tokens.append(self.make_token('t_done', args = {}))
      else:
        new_state = 's_value'
        self.buffer_write(c)
      
      self.lexer.change_state(new_state, c)
      return tokens
  
  class _state_s_done(btl_lexer_state_base):
    def __init__(self, lexer, log_tag):
      name = 's_done'
      super().__init__(lexer, name, log_tag)
  
    def handle_char(self, c):
      self.log_handle_char(c)
  
      new_state = None
      tokens = []
  
      
      self.lexer.change_state(new_state, c)
      return tokens

  def __init__(self, source = None):
    log_tag = f'_fruit_kiwi_lexer'
    desc_text = self._DESC_TEXT
    token = self._token
    states = {
      's_expecting_key': self._state_s_expecting_key(self, log_tag),
      's_expecting_key_error': self._state_s_expecting_key_error(self, log_tag),
      's_key': self._state_s_key(self, log_tag),
      's_value': self._state_s_value(self, log_tag),
      's_done': self._state_s_done(self, log_tag),
    }
    super().__init__(log_tag, desc_text, token, states, source = source)
  _DESC_TEXT = """
#BTL
#
# Key Value pair lexer
#
lexer
  name: keyval
  description: A Key Value pair lexer
  version: 1.0
  start_state: s_expecting_key
  end_state: s_done

tokens
  t_done
    type_hint: h_done
  t_equal
  t_key
  t_line_break
    type_hint: h_line_break
  t_space
  t_value

errors
  unexpected_char: In state {state} unexpected character {char} instead of key

chars
  c_keyval_key_first: c_underscore | c_alpha
  c_keyval_key: c_keyval_key_first | c_numeric

states

  s_expecting_key
    c_eos: s_done
      emit t_done
    c_nl: s_expecting_key
      buffer write
      emit t_line_break
      buffer reset
    c_ws: s_expecting_key
      emit t_space 
    c_keyval_key_first: s_key
      buffer write
    default: s_expecting_key_error
      raise unexpected_char
      
  s_expecting_key_error
    default: s_done
    
  s_key
    c_keyval_key: s_key
      buffer write
    c_equal: s_value
      emit t_key
      buffer reset
      buffer write
      emit t_equal
      buffer reset
    c_eos: s_done
      emit t_key
      buffer reset
      emit t_done
      
  s_value
    c_nl: s_expecting_key
      emit t_value
      buffer reset
      buffer write
      emit t_line_break
      buffer reset
    c_eos: s_done
      emit t_value
      buffer reset
      emit t_done
    default: s_value
      buffer write
      
  s_done

"""
check.register_class(_fruit_kiwi_lexer, include_seq = False)
'''

  _DESC_JSON = '''
{
  "header": {
    "name": "keyval", 
    "description": "A Key Value pair lexer", 
    "version": "1.0", 
    "start_state": "s_expecting_key", 
    "end_state": "s_done"
  }, 
  "tokens": [
    [
      "t_done", 
      {
        "type_hint": "h_done"
      }
    ], 
    [
      "t_equal", 
      {}
    ], 
    [
      "t_key", 
      {}
    ], 
    [
      "t_line_break", 
      {
        "type_hint": "h_line_break"
      }
    ], 
    [
      "t_space", 
      {}
    ], 
    [
      "t_value", 
      {}
    ]
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
              "name": "emit", 
              "command": "t_done", 
              "args": {}
            }
          ]
        }, 
        {
          "to_state": "s_expecting_key", 
          "char_name": "c_nl", 
          "commands": [
            {
              "name": "buffer", 
              "command": "write", 
              "args": {}
            }, 
            {
              "name": "emit", 
              "command": "t_line_break", 
              "args": {}
            }, 
            {
              "name": "buffer", 
              "command": "reset", 
              "args": {}
            }
          ]
        }, 
        {
          "to_state": "s_expecting_key", 
          "char_name": "c_ws", 
          "commands": [
            {
              "name": "emit", 
              "command": "t_space", 
              "args": {}
            }
          ]
        }, 
        {
          "to_state": "s_key", 
          "char_name": "c_keyval_key_first", 
          "commands": [
            {
              "name": "buffer", 
              "command": "write", 
              "args": {}
            }
          ]
        }, 
        {
          "to_state": "s_expecting_key_error", 
          "char_name": "default", 
          "commands": [
            {
              "name": "raise", 
              "command": "unexpected_char", 
              "args": {}
            }
          ]
        }
      ], 
      "is_end_state": false
    }, 
    {
      "name": "s_expecting_key_error", 
      "transitions": [
        {
          "to_state": "s_done", 
          "char_name": "default", 
          "commands": []
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
              "command": "write", 
              "args": {}
            }
          ]
        }, 
        {
          "to_state": "s_value", 
          "char_name": "c_equal", 
          "commands": [
            {
              "name": "emit", 
              "command": "t_key", 
              "args": {}
            }, 
            {
              "name": "buffer", 
              "command": "reset", 
              "args": {}
            }, 
            {
              "name": "buffer", 
              "command": "write", 
              "args": {}
            }, 
            {
              "name": "emit", 
              "command": "t_equal", 
              "args": {}
            }, 
            {
              "name": "buffer", 
              "command": "reset", 
              "args": {}
            }
          ]
        }, 
        {
          "to_state": "s_done", 
          "char_name": "c_eos", 
          "commands": [
            {
              "name": "emit", 
              "command": "t_key", 
              "args": {}
            }, 
            {
              "name": "buffer", 
              "command": "reset", 
              "args": {}
            }, 
            {
              "name": "emit", 
              "command": "t_done", 
              "args": {}
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
              "name": "emit", 
              "command": "t_value", 
              "args": {}
            }, 
            {
              "name": "buffer", 
              "command": "reset", 
              "args": {}
            }, 
            {
              "name": "buffer", 
              "command": "write", 
              "args": {}
            }, 
            {
              "name": "emit", 
              "command": "t_line_break", 
              "args": {}
            }, 
            {
              "name": "buffer", 
              "command": "reset", 
              "args": {}
            }
          ]
        }, 
        {
          "to_state": "s_done", 
          "char_name": "c_eos", 
          "commands": [
            {
              "name": "emit", 
              "command": "t_value", 
              "args": {}
            }, 
            {
              "name": "buffer", 
              "command": "reset", 
              "args": {}
            }, 
            {
              "name": "emit", 
              "command": "t_done", 
              "args": {}
            }
          ]
        }, 
        {
          "to_state": "s_value", 
          "char_name": "default", 
          "commands": [
            {
              "name": "buffer", 
              "command": "write", 
              "args": {}
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
'''

  def test_chars(self):
    desc_text = '''#BTL
lexer
  name: test_lexer
  description: A test lexer
  version: 1.0
  start_state: start
  end_state: end

chars
  test_world: 🌍
  test_minus: -
  test_plus: +
  test_operator: test_plus | test_minus
'''
    desc = btl_lexer_desc.parse_text(desc_text)
    
if __name__ == '__main__':
  unit_test.main()

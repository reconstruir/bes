#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os

from bes.fs.file_util import file_util
from bes.property.cached_class_property import cached_class_property
from bes.system.check import check
from bes.system.execute import execute
from bes.testing.unit_test import unit_test
from bes.text.text_line_parser import text_line_parser

from bes.btl.btl_code_gen_buffer import btl_code_gen_buffer
from bes.btl.btl_error import btl_error
from bes.btl.btl_lexer_error import btl_lexer_error
from bes.btl.btl_lexer_desc import btl_lexer_desc
from bes.btl.btl_lexer_desc_char import btl_lexer_desc_char
from bes.btl.btl_lexer_desc_char_map import btl_lexer_desc_char_map
from bes.btl.btl_lexer_desc_char_map import btl_lexer_desc_char_map
from bes.btl.btl_lexer_desc_state import btl_lexer_desc_state
from bes.btl.btl_lexer_desc_state_transition_command import btl_lexer_desc_state_transition_command
from bes.btl.btl_lexer_desc_state_transition import btl_lexer_desc_state_transition

from _test_simple_lexer_mixin import _test_simple_lexer_mixin

class test_btl_lexer_desc(_test_simple_lexer_mixin, unit_test):

  def test_parse_text_to_json(self):
    #print(btl_lexer_desc.parse_text(self._simple_lexer_desc_text).to_json())
    #return
    self.assert_string_equal_fuzzy(
      self._DESC_JSON,
      btl_lexer_desc.parse_text(self._simple_lexer_desc_text).to_json()
    )

  def test_to_mermaid_diagram(self):
    #print(btl_lexer_desc.parse_text(self._simple_lexer_desc_text).to_mermaid_diagram())
    #return
    self.assert_string_equal_fuzzy( '''\
stateDiagram-v2
  direction LR

  %% s_start state
  [*] --> s_start
  s_start --> s_done: c_eos
  s_start --> s_start: c_line_break
  s_start --> s_start: c_ws
  s_start --> s_key: c_keyval_key_first
  s_start --> s_done: default

  %% s_key state
  s_key --> s_key: c_keyval_key
  s_key --> s_value: c_equal
  s_key --> s_done: c_eos

  %% s_value state
  s_value --> s_start: c_line_break
  s_value --> s_done: c_eos
  s_value --> s_value: default

  %% s_done state
  s_done --> [*]
''', btl_lexer_desc.parse_text(self._simple_lexer_desc_text).to_mermaid_diagram() )

  def test_generate_code(self):
    desc = btl_lexer_desc.parse_text(self._simple_lexer_desc_text)
    actual = self.call_function_with_buf(desc, 'generate_code', '_fruit', 'kiwi_lexer')
    #print(actual)
    #return
    replacements = {}
    #replacements = { ' ': '□' }
    self.assert_python_code_text_equal( self._EXPECTED_CODE, actual, replacements = replacements)

  def test_write_code(self):
    tmp = self.make_temp_file(suffix = '.py')
    desc = btl_lexer_desc.parse_text(self._simple_lexer_desc_text)
    desc.write_code(tmp, '_fruit', 'kiwi_lexer')

    self.assert_python_code_text_equal( self._EXPECTED_CODE, file_util.read(tmp, codec = 'utf-8') )

  @classmethod
  def _add_line_numbers(clazz, code):
    p = text_line_parser(code)
    p.add_line_numbers()
    return str(p)
      
  def test_use_code(self):
    desc = btl_lexer_desc.parse_text(self._simple_lexer_desc_text)
    lexer_code = self.call_function_with_buf(desc, 'generate_code', '_fruit', 'kiwi_lexer')
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
    self.assertEqual( 's_start', l.desc.header.start_state )
    self.assertEqual( 's_done', l.desc.header.end_state )
    self.assertEqual( 's_start', l._states['s_start'].name )

    tokens = l.lex_all(text)
    def _hack_token(token_):
      if token_.name == 't_line_break':
        return token_.clone(mutations = { 'value': '\\n' })
      return token_
    hacked_tokens = [ _hack_token(token) for token in tokens ]
    expected = [
      '0: t_line_break:\\n:p=1,1:h=h_line_break',
      '1: t_key:fruit:p=2,1',
      '2: t_key_value_delimiter:=:p=2,6',
      '3: t_value:kiwi:p=2,7',
      '4: t_line_break:\\n:p=2,11:h=h_line_break',
      '5: t_key:color:p=3,1',
      '6: t_key_value_delimiter:=:p=3,6',
      '7: t_value:green:p=3,7',
      '8: t_line_break:\\n:p=3,12:h=h_line_break',
      '9: t_key:taste:p=4,1',
      '10: t_key_value_delimiter:=:p=4,6',
      '11: t_value:sour:p=4,7',
      '12: t_line_break:\\n:p=4,11:h=h_line_break',
      '13: t_done::h=h_done',
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
    desc = btl_lexer_desc.parse_text(self._simple_lexer_desc_text)
    actual = desc.to_json()
    #print(actual)
    #return
    self.assert_json_equal( self._DESC_JSON, actual )

  @cached_class_property
  def _EXPECTED_CODE(clazz):
    return clazz._EXPECTED_CODE_TEMPLATE.replace('@@@_DESC_TEXT@@@', clazz._simple_lexer_desc_text)
    
  _EXPECTED_CODE_TEMPLATE = '''
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.btl.btl_lexer_base import btl_lexer_base
from bes.btl.btl_lexer_runtime_error import btl_lexer_runtime_error
from bes.btl.btl_lexer_state_base import btl_lexer_state_base
from bes.btl.btl_lexer_token import btl_lexer_token

class _fruit_kiwi_lexer(btl_lexer_base):

  class _token:

    T_DONE = 't_done'
    T_KEY = 't_key'
    T_KEY_VALUE_DELIMITER = 't_key_value_delimiter'
    T_LINE_BREAK = 't_line_break'
    T_SPACE = 't_space'
    T_VALUE = 't_value'

  class e_unexpected_char(btl_lexer_runtime_error):
    def __init__(self, message = None):
      super().__init__(message = message)

  
  class _state_s_start(btl_lexer_state_base):
    def __init__(self, lexer, log_tag):
      name = 's_start'
      super().__init__(lexer, name, log_tag)
  
    def handle_char(self, context, c):
      self.log_handle_char(context, c)
  
      new_state_name = None
      tokens = []
  
      if self.char_in(c, 'c_eos'):
        new_state_name = 's_done'
        tokens.append(self.make_token(context, 't_done', args = {}))
      elif self.char_in(c, 'c_line_break'):
        new_state_name = 's_start'
        context.buffer_write(c)
        tokens.append(self.make_token(context, 't_line_break', args = {}))
        context.buffer_reset()
      elif self.char_in(c, 'c_ws'):
        new_state_name = 's_start'
        tokens.append(self.make_token(context, 't_space', args = {}))
      elif self.char_in(c, 'c_keyval_key_first'):
        new_state_name = 's_key'
        context.buffer_write(c)
      else:
        new_state_name = 's_done'
        state_name = self.name
        char = c
        msg = f'In state "{state_name}" unexpected character: "{char}"'
        raise self.lexer.e_unexpected_char(message = msg)
      
      return self._handle_char_result(new_state_name, tokens)
  
  class _state_s_key(btl_lexer_state_base):
    def __init__(self, lexer, log_tag):
      name = 's_key'
      super().__init__(lexer, name, log_tag)
  
    def handle_char(self, context, c):
      self.log_handle_char(context, c)
  
      new_state_name = None
      tokens = []
  
      if self.char_in(c, 'c_keyval_key'):
        new_state_name = 's_key'
        context.buffer_write(c)
      elif self.char_in(c, 'c_equal'):
        new_state_name = 's_value'
        tokens.append(self.make_token(context, 't_key', args = {}))
        context.buffer_reset()
        context.buffer_write(c)
        tokens.append(self.make_token(context, 't_key_value_delimiter', args = {}))
        context.buffer_reset()
      elif self.char_in(c, 'c_eos'):
        new_state_name = 's_done'
        tokens.append(self.make_token(context, 't_key', args = {}))
        context.buffer_reset()
        tokens.append(self.make_token(context, 't_done', args = {}))
      
      return self._handle_char_result(new_state_name, tokens)
  
  class _state_s_value(btl_lexer_state_base):
    def __init__(self, lexer, log_tag):
      name = 's_value'
      super().__init__(lexer, name, log_tag)
  
    def handle_char(self, context, c):
      self.log_handle_char(context, c)
  
      new_state_name = None
      tokens = []
  
      if self.char_in(c, 'c_line_break'):
        new_state_name = 's_start'
        tokens.append(self.make_token(context, 't_value', args = {}))
        context.buffer_reset()
        context.buffer_write(c)
        tokens.append(self.make_token(context, 't_line_break', args = {}))
        context.buffer_reset()
      elif self.char_in(c, 'c_eos'):
        new_state_name = 's_done'
        tokens.append(self.make_token(context, 't_value', args = {}))
        context.buffer_reset()
        tokens.append(self.make_token(context, 't_done', args = {}))
      else:
        new_state_name = 's_value'
        context.buffer_write(c)
      
      return self._handle_char_result(new_state_name, tokens)
  
  class _state_s_done(btl_lexer_state_base):
    def __init__(self, lexer, log_tag):
      name = 's_done'
      super().__init__(lexer, name, log_tag)
  
    def handle_char(self, context, c):
      self.log_handle_char(context, c)
  
      new_state_name = None
      tokens = []
  
      
      return self._handle_char_result(new_state_name, tokens)

  def __init__(self, desc_source = None):
    log_tag = f'_fruit_kiwi_lexer'
    desc_text = self._DESC_TEXT
    token = self._token
    states = {
      's_start': self._state_s_start(self, log_tag),
      's_key': self._state_s_key(self, log_tag),
      's_value': self._state_s_value(self, log_tag),
      's_done': self._state_s_done(self, log_tag),
    }
    super().__init__(log_tag, desc_text, token, states, desc_source = desc_source)
  _DESC_TEXT = """
#BTL
#
# Key Value pair lexer
#
lexer
  name: l_simple
  description: A simple key value pair lexer
  version: 1.0
  start_state: s_start
  end_state: s_done

tokens
  t_done
    type_hint: h_done
  t_key_value_delimiter
  t_key
  t_line_break
    type_hint: h_line_break
  t_space
  t_value

errors
  e_unexpected_char: In state "{state_name}" unexpected character: "{char}"

chars
  c_keyval_key_first: c_underscore | c_alpha
  c_keyval_key: c_keyval_key_first | c_numeric

states

  s_start
    c_eos: s_done
      emit t_done
    c_line_break: s_start
      buffer write
      emit t_line_break
      buffer reset
    c_ws: s_start
      emit t_space 
    c_keyval_key_first: s_key
      buffer write
    default: s_done
      error e_unexpected_char
      
  s_key
    c_keyval_key: s_key
      buffer write
    c_equal: s_value
      emit t_key
      buffer reset
      buffer write
      emit t_key_value_delimiter
      buffer reset
    c_eos: s_done
      emit t_key
      buffer reset
      emit t_done
      
  s_value
    c_line_break: s_start
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

  _DESC_JSON = r'''
{
  "header": {
    "name": "l_simple", 
    "description": "A simple key value pair lexer", 
    "version": "1.0", 
    "start_state": "s_start", 
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
      "t_key", 
      {}
    ], 
    [
      "t_key_value_delimiter", 
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
      "name": "e_unexpected_char", 
      "message": "In state \"{state_name}\" unexpected character: \"{char}\""
    }
  ], 
  "char_map": {
    "c_keyval_key_first": {
      "name": "c_keyval_key_first", 
      "chars": [
        "A", 
        "B", 
        "C", 
        "D", 
        "E", 
        "F", 
        "G", 
        "H", 
        "I", 
        "J", 
        "K", 
        "L", 
        "M", 
        "N", 
        "O", 
        "P", 
        "Q", 
        "R", 
        "S", 
        "T", 
        "U", 
        "V", 
        "W", 
        "X", 
        "Y", 
        "Z", 
        "_", 
        "a", 
        "b", 
        "c", 
        "d", 
        "e", 
        "f", 
        "g", 
        "h", 
        "i", 
        "j", 
        "k", 
        "l", 
        "m", 
        "n", 
        "o", 
        "p", 
        "q", 
        "r", 
        "s", 
        "t", 
        "u", 
        "v", 
        "w", 
        "x", 
        "y", 
        "z"
      ]
    }, 
    "c_keyval_key": {
      "name": "c_keyval_key", 
      "chars": [
        "0", 
        "1", 
        "2", 
        "3", 
        "4", 
        "5", 
        "6", 
        "7", 
        "8", 
        "9", 
        "A", 
        "B", 
        "C", 
        "D", 
        "E", 
        "F", 
        "G", 
        "H", 
        "I", 
        "J", 
        "K", 
        "L", 
        "M", 
        "N", 
        "O", 
        "P", 
        "Q", 
        "R", 
        "S", 
        "T", 
        "U", 
        "V", 
        "W", 
        "X", 
        "Y", 
        "Z", 
        "_", 
        "a", 
        "b", 
        "c", 
        "d", 
        "e", 
        "f", 
        "g", 
        "h", 
        "i", 
        "j", 
        "k", 
        "l", 
        "m", 
        "n", 
        "o", 
        "p", 
        "q", 
        "r", 
        "s", 
        "t", 
        "u", 
        "v", 
        "w", 
        "x", 
        "y", 
        "z"
      ]
    }
  }, 
  "states": [
    {
      "name": "s_start", 
      "transitions": [
        {
          "to_state": "s_done", 
          "char_name": "c_eos", 
          "commands": [
            {
              "name": "emit", 
              "action": "t_done", 
              "args": {}
            }
          ]
        }, 
        {
          "to_state": "s_start", 
          "char_name": "c_line_break", 
          "commands": [
            {
              "name": "buffer", 
              "action": "write", 
              "args": {}
            }, 
            {
              "name": "emit", 
              "action": "t_line_break", 
              "args": {}
            }, 
            {
              "name": "buffer", 
              "action": "reset", 
              "args": {}
            }
          ]
        }, 
        {
          "to_state": "s_start", 
          "char_name": "c_ws", 
          "commands": [
            {
              "name": "emit", 
              "action": "t_space", 
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
              "action": "write", 
              "args": {}
            }
          ]
        }, 
        {
          "to_state": "s_done", 
          "char_name": "default", 
          "commands": [
            {
              "name": "error", 
              "action": "e_unexpected_char", 
              "args": {}
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
              "action": "write", 
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
              "action": "t_key", 
              "args": {}
            }, 
            {
              "name": "buffer", 
              "action": "reset", 
              "args": {}
            }, 
            {
              "name": "buffer", 
              "action": "write", 
              "args": {}
            }, 
            {
              "name": "emit", 
              "action": "t_key_value_delimiter", 
              "args": {}
            }, 
            {
              "name": "buffer", 
              "action": "reset", 
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
              "action": "t_key", 
              "args": {}
            }, 
            {
              "name": "buffer", 
              "action": "reset", 
              "args": {}
            }, 
            {
              "name": "emit", 
              "action": "t_done", 
              "args": {}
            }
          ]
        }
      ]
    }, 
    {
      "name": "s_value", 
      "transitions": [
        {
          "to_state": "s_start", 
          "char_name": "c_line_break", 
          "commands": [
            {
              "name": "emit", 
              "action": "t_value", 
              "args": {}
            }, 
            {
              "name": "buffer", 
              "action": "reset", 
              "args": {}
            }, 
            {
              "name": "buffer", 
              "action": "write", 
              "args": {}
            }, 
            {
              "name": "emit", 
              "action": "t_line_break", 
              "args": {}
            }, 
            {
              "name": "buffer", 
              "action": "reset", 
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
              "action": "t_value", 
              "args": {}
            }, 
            {
              "name": "buffer", 
              "action": "reset", 
              "args": {}
            }, 
            {
              "name": "emit", 
              "action": "t_done", 
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
              "action": "write", 
              "args": {}
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

  def test_invalild_command_name(self):
    desc_text = '''#BTL
lexer
  name: test_lexer
  description: A test lexer
  version: 1.0
  start_state: start
  end_state: end

states

  s_start
    c_eos: s_done
      notgood
'''
    with self.assertRaises(btl_lexer_error) as ctx:
      desc = btl_lexer_desc.parse_text(desc_text)
    self.assertEqual( 'Missing arguments for command: "notgood" - line 13', ctx.exception.message )

  def test_invalild_command_action(self):
    desc_text = '''#BTL
lexer
  name: test_lexer
  description: A test lexer
  version: 1.0
  start_state: start
  end_state: end

states

  s_start
    c_eos: s_done
      buffer notgood
    default: s_done
      error e_unexpected_char
'''
    desc = btl_lexer_desc.parse_text(desc_text)
    buf = btl_code_gen_buffer()
    with self.assertRaises(btl_lexer_error) as ctx:
      desc.generate_code(buf, 'fruit', 'kiwi')
    self.assertEqual( 'Unknown command action: "notgood"', ctx.exception.message )
    
if __name__ == '__main__':
  unit_test.main()

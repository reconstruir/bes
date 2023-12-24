#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.b_text_lexer.btl_code_gen import btl_code_gen
from bes.b_text_lexer.btl_code_gen_buffer import btl_code_gen_buffer
from bes.b_text_lexer.btl_desc import btl_desc
from bes.b_text_lexer.btl_desc import btl_desc
from bes.b_text_lexer.btl_desc_char import btl_desc_char
from bes.b_text_lexer.btl_desc_char_map import btl_desc_char_map
from bes.b_text_lexer.btl_desc_state import btl_desc_state
from bes.b_text_lexer.btl_desc_state_command import btl_desc_state_command
from bes.b_text_lexer.btl_desc_state_transition import btl_desc_state_transition
from bes.b_text_lexer.btl_error import btl_error
from bes.testing.unit_test import unit_test

from keyval_desc_mixin import keyval_desc_mixin

class test_btl_code_gen(keyval_desc_mixin, unit_test):
  
  @classmethod
  def _call__make_state_command_code(clazz, *args, **kwargs):
    return clazz._call_func('_make_state_command_code', *args, **kwargs)

  @classmethod
  def _call__make_transition_code(clazz, *args, **kwargs):
    return clazz._call_func('_make_transition_code', *args, **kwargs)

  @classmethod
  def _call__make_state_class_code(clazz, *args, **kwargs):
    return clazz._call_func('_make_state_class_code', *args, **kwargs)

  @classmethod
  def _call__make_token_class_code(clazz, *args, **kwargs):
    return clazz._call_func('_make_token_class_code', *args, **kwargs)
  
  @classmethod
  def _call__make_state_machine_code(clazz, *args, **kwargs):
    return clazz._call_func('_make_state_machine_code', *args, **kwargs)
  
  @classmethod
  def _call_func(clazz, func_name, *args, **kwargs):
    buf = btl_code_gen_buffer()
    func = getattr(btl_code_gen, func_name)
    func(buf, *args, **kwargs)
    return buf.get_value()
  
  def test__make_state_class_code(self):
    char_map = btl_desc_char_map()
    cmd = btl_desc_state_command('yield', 't_cheese')
    transition = btl_desc_state_transition('s_juice', 'c_equal', [ cmd ])
    state = btl_desc_state('s_juice', [ transition ])

    self.assert_code_equal('''
class fruit_kiwi_lexer_state_s_juice(btl_lexer_state_base):
  def __init__(self, lexer):
    super().__init__(lexer)

  def handle_char(self, c):
    self.log_handle_char(c)

    new_state = None
    tokens = []

    if c in {61}:
      new_state = s_juice
      tokens.append(self.make_token(t_cheese, self.buffer_value(), self.position)
    
    self.lexer.change_state(new_state, c)
    return tokens
''', self._call__make_state_class_code('fruit', 'kiwi', char_map, state) )
    
  def test__make_transition_code(self):
    char_map = btl_desc_char_map()
    cmd = btl_desc_state_command('yield', 't_cheese')
    transition = btl_desc_state_transition('s_kiwi', 'c_equal', [ cmd ])
    
    self.assert_code_equal('''
if c in {61}:
  new_state = s_kiwi
  tokens.append(self.make_token(t_cheese, self.buffer_value(), self.position)
''', self._call__make_transition_code(char_map, transition) )

  
  def test__make_state_command_code_yield(self):
    cmd = btl_desc_state_command('yield', 't_cheese')
    self.assert_code_equal( '''
tokens.append(self.make_token(t_cheese, self.buffer_value(), self.position)
''', self._call__make_state_command_code(cmd) )

  def test__make_state_command_code_buffer_write(self):
    cmd = btl_desc_state_command('buffer', 'write')
    self.assert_code_equal( '''
self.lexer.buffer_write(c)
''', self._call__make_state_command_code(cmd) )

  def test__make_state_command_code_buffer_reset(self):
    cmd = btl_desc_state_command('buffer', 'reset')
    self.assert_code_equal( '''
self.lexer.buffer_reset()
''', self._call__make_state_command_code(cmd) )

  def test__make_state_command_code_buffer_error(self):
    cmd = btl_desc_state_command('buffer', 'notthere')
    self.assert_code_equal( '''
raise btl_lexer_error('Unknown buffer command: "notthere"')
''', self._call__make_state_command_code(cmd) )

  def test__make_token_class_code(self):
    self.assert_code_equal('''
class fruit_kiwi_lexer_token(object):

  KIWI = 'kiwi'
  LEMON = 'lemon'
  MELON = 'melon'
  
  def __init__(self, lexer):
    check.check_text_lexer(lexer)
  
    self._lexer = lexer
  
  def make_kiwi(self, value, position):
    return lexer_token(self.KIWI, value, self._lexer.position)
  
  def make_lemon(self, value, position):
    return lexer_token(self.LEMON, value, self._lexer.position)
  
  def make_melon(self, value, position):
    return lexer_token(self.MELON, value, self._lexer.position)
''', self._call__make_token_class_code('fruit', 'kiwi', { 'kiwi', 'lemon', 'melon' }) )

  def test__make_state_machine_code(self):
    desc = btl_desc.parse_text(self._keyval_desc_text)
    self.assert_code_equal('''
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.b_text_lexer.btl_lexer_base import btl_lexer_base
from bes.b_text_lexer.btl_lexer_state_base import btl_lexer_state_base


class fruit_kiwi_lexer_token(object):

  T_DONE = 't_done'
  T_EXPECTING_KEY = 't_expecting_key'
  T_KEY = 't_key'
  T_LINE_BREAK = 't_line_break'
  T_SPACE = 't_space'
  T_VALUE = 't_value'
  
  def __init__(self, lexer):
    check.check_text_lexer(lexer)
  
    self._lexer = lexer
  
  def make_t_done(self, value, position):
    return lexer_token(self.T_DONE, value, self._lexer.position)
  
  def make_t_expecting_key(self, value, position):
    return lexer_token(self.T_EXPECTING_KEY, value, self._lexer.position)
  
  def make_t_key(self, value, position):
    return lexer_token(self.T_KEY, value, self._lexer.position)
  
  def make_t_line_break(self, value, position):
    return lexer_token(self.T_LINE_BREAK, value, self._lexer.position)
  
  def make_t_space(self, value, position):
    return lexer_token(self.T_SPACE, value, self._lexer.position)
  
  def make_t_value(self, value, position):
    return lexer_token(self.T_VALUE, value, self._lexer.position)
    


class fruit_kiwi_lexer_state_s_expecting_key(btl_lexer_state_base):
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

class fruit_kiwi_lexer_state_s_key(btl_lexer_state_base):
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

class fruit_kiwi_lexer_state_s_value(btl_lexer_state_base):
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

class fruit_kiwi_lexer_state_s_done(btl_lexer_state_base):
  def __init__(self, lexer):
    super().__init__(lexer)

  def handle_char(self, c):
    self.log_handle_char(c)

    new_state = None
    tokens = []

    
    self.lexer.change_state(new_state, c)
    return tokens
''', self._call__make_state_machine_code('fruit', 'kiwi', desc) )
    
if __name__ == '__main__':
  unit_test.main()

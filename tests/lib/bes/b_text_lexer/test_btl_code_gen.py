#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.b_text_lexer.btl_code_gen import btl_code_gen
from bes.b_text_lexer.btl_code_gen_buffer import btl_code_gen_buffer
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
    print(self._call__make_token_class_code('fruit', 'kiwi', { 'kiwi', 'lemon', 'melon' }))
    return
#    char_map = btl_desc_char_map()
#    cmd = btl_desc_state_command('yield', 't_cheese')
#    transition = btl_desc_state_transition('s_juice', 'c_equal', [ cmd ])
#    state = btl_desc_state('s_juice', [ transition ])

    self.assert_code_equal('''
class fruit_kiwi_lexer_token(object):

  def __init__(self, lexer):
    check.check_text_lexer(lexer)

    self._lexer = lexer
''', self._call__make_token_class_code('fruit', 'kiwi', { 'kiwi', 'lemon', 'melon' }) )
    
if __name__ == '__main__':
  unit_test.main()

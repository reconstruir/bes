#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.b_text_lexer.btl_desc import btl_desc
from bes.b_text_lexer.btl_code_gen import btl_code_gen
from bes.b_text_lexer.btl_desc_state_transition import btl_desc_state_transition
from bes.b_text_lexer.btl_desc_char_map import btl_desc_char_map
#from bes.b_text_lexer.btl_desc_char import btl_desc_char
from bes.b_text_lexer.btl_desc_state_command import btl_desc_state_command
from bes.b_text_lexer.btl_error import btl_error
from bes.testing.unit_test import unit_test

from keyval_desc_mixin import keyval_desc_mixin

class test_btl_code_gen(keyval_desc_mixin, unit_test):

  def xtest_make_state_class_code(self):
    desc = btl_desc.parse_text(self._keyval_desc_text)
    self.assertEqual('''
caca
''', btl_code_gen.make_state_class_code(desc, desc.states[0]) )

  def test__make_transition_code(self):
    char_map = btl_desc_char_map()
    cmd = btl_desc_state_command('yield', 't_cheese')
    transition = btl_desc_state_transition('s_kiwi', 'c_equal', [ cmd ])
    
    self.assert_code_equal('''
if c in {61}:
  new_state = s_kiwi
  tokens.append(self.make_token(t_cheese, self.buffer_value(), self.position)
''', btl_code_gen._make_transition_code(char_map, transition) )

  def test__make_state_command_code_yield(self):
    cmd = btl_desc_state_command('yield', 't_cheese')
    self.assert_code_equal( '''
tokens.append(self.make_token(t_cheese, self.buffer_value(), self.position)
''', btl_code_gen._make_state_command_code(cmd) )

  def test__make_state_command_code_buffer_write(self):
    cmd = btl_desc_state_command('buffer', 'write')
    self.assert_code_equal( '''
self.lexer.buffer_write(c)
''', btl_code_gen._make_state_command_code(cmd) )

  def test__make_state_command_code_buffer_reset(self):
    cmd = btl_desc_state_command('buffer', 'reset')
    self.assert_code_equal( '''
self.lexer.buffer_reset()
''', btl_code_gen._make_state_command_code(cmd) )

  def test__make_state_command_code_buffer_error(self):
    #desc = btl_desc.parse_text(self._keyval_desc_text)
    cmd = btl_desc_state_command('buffer', 'notthere')
    self.assert_code_equal( '''
raise btl_lexer_error('Unknown buffer command: "notthere"')
''', btl_code_gen._make_state_command_code(cmd) )
    
  def assert_code_equal(self, expected, actual):
    return self.assert_string_equal(expected, actual,
                                    strip = True,
                                    multi_line = True,
                                    ignore_white_space = False,
                                    native_line_breaks = True)
    
if __name__ == '__main__':
  unit_test.main()

#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.b_text_lexer.btl_desc_char_map import btl_desc_char_map
from bes.b_text_lexer.btl_desc_state import btl_desc_state
from bes.b_text_lexer.btl_desc_state_command import btl_desc_state_command
from bes.b_text_lexer.btl_desc_state_transition import btl_desc_state_transition
from bes.b_text_lexer.btl_error import btl_error
from bes.testing.unit_test import unit_test
from bes.text.tree_text_parser import _text_node_data

from keyval_desc_mixin import keyval_desc_mixin

class test_btl_desc_state(keyval_desc_mixin, unit_test):

  def test_generate_code(self):
    char_map = btl_desc_char_map()
    cmd = btl_desc_state_command('yield', 't_cheese')
    transition = btl_desc_state_transition('s_juice', 'c_equal', [ cmd ])
    state = btl_desc_state('s_juice', [ transition ], False)

    self.assert_code_equal('''
class _fruit_kiwi_lexer_state_s_juice(btl_lexer_state_base):
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
''', self.call_buf_func(state, 'generate_code', '_fruit', 'kiwi', char_map) )
  
if __name__ == '__main__':
  unit_test.main()

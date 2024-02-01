#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.btl.btl_parser_desc_char_map import btl_parser_desc_char_map
from bes.btl.btl_parser_desc_state import btl_parser_desc_state
from bes.btl.btl_parser_desc_state_command import btl_parser_desc_state_command
from bes.btl.btl_parser_desc_state_transition import btl_parser_desc_state_transition
from bes.btl.btl_error import btl_error
from bes.testing.unit_test import unit_test
from bes.text.tree_text_parser import _text_node_data

from _test_lexer_desc_mixin import _test_lexer_desc_mixin

class test_btl_parser_desc_state(_test_lexer_desc_mixin, unit_test):

  def test_generate_code(self):
    char_map = btl_parser_desc_char_map()
    cmd = btl_parser_desc_state_command('emit', 't_cheese', {})
    transition = btl_parser_desc_state_transition('s_juice', 'c_equal', [ cmd ])
    state = btl_parser_desc_state('s_juice', [ transition ], False)

    self.assert_code_equal('''
class _state_s_juice(btl_parser_state_base):
  def __init__(self, lexer, log_tag):
    name = 's_juice'
    super().__init__(lexer, name, log_tag)

  def handle_char(self, c):
    self.log_handle_char(c)

    new_state = None
    tokens = []

    if self.char_in(c, 'c_equal'):
      new_state = 's_juice'
      tokens.append(self.make_token('t_cheese', args = {}))
    
    self.lexer.change_state(new_state, c)
    return tokens
''', self.call_buf_func(state, 'generate_code', char_map) )
  
if __name__ == '__main__':
  unit_test.main()

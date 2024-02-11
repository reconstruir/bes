#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.btl.btl_lexer_desc_char_map import btl_lexer_desc_char_map
from bes.btl.btl_lexer_desc_state import btl_lexer_desc_state
from bes.btl.btl_lexer_desc_state_transition_command import btl_lexer_desc_state_transition_command
from bes.btl.btl_lexer_desc_state_transition import btl_lexer_desc_state_transition
from bes.btl.btl_error import btl_error
from bes.testing.unit_test import unit_test

from _test_simple_lexer_mixin import _test_simple_lexer_mixin

class test_btl_lexer_desc_state(_test_simple_lexer_mixin, unit_test):

  def test_generate_code(self):
    char_map = btl_lexer_desc_char_map()
    cmd = btl_lexer_desc_state_transition_command('emit', 't_cheese', {})
    transition = btl_lexer_desc_state_transition('s_juice', 'c_equal', [ cmd ])
    state = btl_lexer_desc_state('s_juice', [ transition ])

    self.assert_python_code_text_equal('''
class _state_s_juice(btl_lexer_state_base):
  def __init__(self, lexer, log_tag):
    name = 's_juice'
    super().__init__(lexer, name, log_tag)

  def handle_char(self, c, options):
    self.log_handle_char(c, options)

    new_state_name = None
    tokens = []

    if self.char_in(c, 'c_equal'):
      new_state_name = 's_juice'
      tokens.append(self.make_token('t_cheese', args = {}))
    
    return self._handle_char_result(new_state_name, tokens)
''', self.call_function_with_buf(state, 'generate_code', [], char_map) )
  
if __name__ == '__main__':
  unit_test.main()

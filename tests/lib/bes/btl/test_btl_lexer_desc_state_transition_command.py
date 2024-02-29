#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.btl.btl_lexer_desc_state_transition_command import btl_lexer_desc_state_transition_command
from bes.btl.btl_error import btl_error
from bes.btl.btl_lexer_error import btl_lexer_error
from bes.testing.unit_test import unit_test

from _test_simple_lexer_mixin import _test_simple_lexer_mixin

class test_btl_lexer_desc_state_transition_command(_test_simple_lexer_mixin, unit_test):

  def test_generate_code_with_emit(self):
    cmd = btl_lexer_desc_state_transition_command('emit', 't_cheese', {})
    self.assert_python_code_text_equal( '''
tokens.append(self.make_token(context, 't_cheese', args = {}))
''', self.call_function_with_buf(cmd, 'generate_code', []) )

  def test_generate_code_with_emit_and_variable(self):
    cmd = btl_lexer_desc_state_transition_command('emit', '${token_name}', {})
    self.assert_python_code_text_equal( '''
tokens.append(self.make_token(context, token_name, args = {}))
''', self.call_function_with_buf(cmd, 'generate_code', []) )
    
  def test_generate_code_with_buffer_write(self):
    cmd = btl_lexer_desc_state_transition_command('buffer', 'write', {})
    self.assert_python_code_text_equal( '''
context.buffer_write(c)
''', self.call_function_with_buf(cmd, 'generate_code', []) )

  def test_generate_code_with_buffer_reset(self):
    cmd = btl_lexer_desc_state_transition_command('buffer', 'reset', {})
    self.assert_python_code_text_equal( '''
context.buffer_reset()
''', self.call_function_with_buf(cmd, 'generate_code', []) )

  def test_generate_code_with_buffer_unknown_action(self):
    cmd = btl_lexer_desc_state_transition_command('buffer', 'notthere', {})

    with self.assertRaises(btl_lexer_error) as ctx:
      self.call_function_with_buf(cmd, 'generate_code', [])
    self.assertEqual( 'Unknown command action: "notthere"', ctx.exception.message )
    
if __name__ == '__main__':
  unit_test.main()

#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.btl.btl_lexer_desc_state_command import btl_lexer_desc_state_command
from bes.btl.btl_error import btl_error
from bes.btl.btl_lexer_error import btl_lexer_error
from bes.testing.unit_test import unit_test
from bes.text.tree_text_parser import _text_node_data

from _test_lexer_desc_mixin import _test_lexer_desc_mixin

class test_btl_lexer_desc_state_command(_test_lexer_desc_mixin, unit_test):

  def test_generate_code_with_emit(self):
    cmd = btl_lexer_desc_state_command('emit', 't_cheese', {})
    self.assert_code_equal( '''
tokens.append(self.make_token('t_cheese', args = {}))
''', self.call_buf_func(cmd, 'generate_code', []) )

  def test_generate_code_with_buffer_write(self):
    cmd = btl_lexer_desc_state_command('buffer', 'write', {})
    self.assert_code_equal( '''
self.buffer_write(c)
''', self.call_buf_func(cmd, 'generate_code', []) )

  def test_generate_code_with_buffer_reset(self):
    cmd = btl_lexer_desc_state_command('buffer', 'reset', {})
    self.assert_code_equal( '''
self.buffer_reset()
''', self.call_buf_func(cmd, 'generate_code', []) )

  def test_generate_code_with_buffer_unknown_action(self):
    cmd = btl_lexer_desc_state_command('buffer', 'notthere', {})

    with self.assertRaises(btl_lexer_error) as ctx:
      self.call_buf_func(cmd, 'generate_code', [])
    self.assertEqual( 'Unknown command action: "notthere"', ctx.exception.message )
    
if __name__ == '__main__':
  unit_test.main()

#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.b_text_lexer.btl_desc_state_command import btl_desc_state_command
from bes.b_text_lexer.btl_error import btl_error
from bes.testing.unit_test import unit_test
from bes.text.tree_text_parser import _text_node_data

from keyval_desc_mixin import keyval_desc_mixin

class test_btl_desc_state_command(keyval_desc_mixin, unit_test):

  def test_write_to_buffer_with_yield(self):
    cmd = btl_desc_state_command('yield', 't_cheese')
    self.assert_code_equal( '''
tokens.append(self.make_token(t_cheese, self.buffer_value(), self.position)
''', self.call_buf_func(cmd, 'write_to_buffer') )

  def test_write_to_buffer_with_buffer_write(self):
    cmd = btl_desc_state_command('buffer', 'write')
    self.assert_code_equal( '''
self.lexer.buffer_write(c)
''', self.call_buf_func(cmd, 'write_to_buffer') )

  def test_write_to_buffer_with_buffer_reset(self):
    cmd = btl_desc_state_command('buffer', 'reset')
    self.assert_code_equal( '''
self.lexer.buffer_reset()
''', self.call_buf_func(cmd, 'write_to_buffer') )

  def test_write_to_buffer_with_buffer_error(self):
    cmd = btl_desc_state_command('buffer', 'notthere')
    self.assert_code_equal( '''
raise btl_lexer_error('Unknown buffer command: "notthere"')
''', self.call_buf_func(cmd, 'write_to_buffer') )
    
if __name__ == '__main__':
  unit_test.main()

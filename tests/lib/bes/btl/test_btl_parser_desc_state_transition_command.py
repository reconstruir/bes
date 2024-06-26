#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.btl.btl_parser_desc_state_transition_command import btl_parser_desc_state_transition_command
from bes.btl.btl_error import btl_error
from bes.testing.unit_test import unit_test
from bes.testing.unit_test_class_skip import unit_test_class_skip

from _test_simple_parser_mixin import _test_simple_parser_mixin

class test_btl_parser_desc_state_transition_command(_test_simple_parser_mixin, unit_test):

  @classmethod
  def setUpClass(clazz):
    unit_test_class_skip.raise_skip('BTL_FIXME')
  
  def test_generate_code_with_emit(self):
    cmd = btl_parser_desc_state_transition_command('emit', 't_cheese', {})
    self.assert_python_code_text_equal( '''
tokens.append(self.make_token('t_cheese', args = {}))
''', self.call_function_with_buf(cmd, 'generate_code', []) )

  def test_generate_code_with_buffer_write(self):
    cmd = btl_parser_desc_state_transition_command('buffer', 'write', {})
    self.assert_python_code_text_equal( '''
self.buffer_write(c)
''', self.call_function_with_buf(cmd, 'generate_code', []) )

  def test_generate_code_with_buffer_reset(self):
    cmd = btl_parser_desc_state_transition_command('buffer', 'reset', {})
    self.assert_python_code_text_equal( '''
self.buffer_reset()
''', self.call_function_with_buf(cmd, 'generate_code', []) )

  def test_generate_code_with_buffer_error(self):
    cmd = btl_parser_desc_state_transition_command('buffer', 'notthere', {})
    self.assert_python_code_text_equal( '''
raise btl_parser_error('Unknown buffer command: "notthere"')
''', self.call_function_with_buf(cmd, 'generate_code', []) )
    
if __name__ == '__main__':
  unit_test.main()

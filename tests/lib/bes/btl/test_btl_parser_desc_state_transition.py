 #!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.btl.btl_parser_desc_state_transition_command import btl_parser_desc_state_transition_command
from bes.btl.btl_parser_desc_state_transition import btl_parser_desc_state_transition
from bes.btl.btl_error import btl_error
from bes.testing.unit_test import unit_test
from bes.testing.unit_test_class_skip import unit_test_class_skip

from _test_simple_parser_mixin import _test_simple_parser_mixin

class test_btl_parser_desc_state_transition(_test_simple_parser_mixin, unit_test):

  @classmethod
  def setUpClass(clazz):
    unit_test_class_skip.raise_skip('BTL_FIXME')

  """
  def test_generate_code(self):
    char_map = btl_parser_desc_char_map()
    cmd = btl_parser_desc_state_transition_command('emit', 't_cheese', {})
    transition = btl_parser_desc_state_transition('s_kiwi', 'c_equal', [ cmd ])
    
    self.assert_python_code_text_equal('''
if self.char_in(c, 'c_equal'):
  new_state = 's_kiwi'
  tokens.append(self.make_token('t_cheese', args = {}))
''', self.call_function_with_buf(transition, 'generate_code', [], char_map, 0, 2) )

  def test_generate_code_with_index_non_zero(self):
    char_map = btl_parser_desc_char_map()
    cmd = btl_parser_desc_state_transition_command('emit', 't_cheese', {})
    transition = btl_parser_desc_state_transition('s_kiwi', 'c_equal', [ cmd ])
    
    self.assert_python_code_text_equal('''
elif self.char_in(c, 'c_equal'):
  new_state = 's_kiwi'
  tokens.append(self.make_token('t_cheese', args = {}))
''', self.call_function_with_buf(transition, 'generate_code', [], char_map, 1, 2) )
"""
  
if __name__ == '__main__':
  unit_test.main()

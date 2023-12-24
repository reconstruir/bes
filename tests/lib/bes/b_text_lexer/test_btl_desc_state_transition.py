 #!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.b_text_lexer.btl_desc_state_command import btl_desc_state_command
from bes.b_text_lexer.btl_desc_state_transition import btl_desc_state_transition
from bes.b_text_lexer.btl_error import btl_error
from bes.b_text_lexer.btl_desc_char_map import btl_desc_char_map
from bes.testing.unit_test import unit_test
from bes.text.tree_text_parser import _text_node_data

from keyval_desc_mixin import keyval_desc_mixin

class test_btl_desc_state_transition(keyval_desc_mixin, unit_test):

  def test_write_to_buffer(self):
    char_map = btl_desc_char_map()
    cmd = btl_desc_state_command('yield', 't_cheese')
    transition = btl_desc_state_transition('s_kiwi', 'c_equal', [ cmd ])
    
    self.assert_code_equal('''
if c in {61}:
  new_state = s_kiwi
  tokens.append(self.make_token(t_cheese, self.buffer_value(), self.position)
''', self.call_buf_func(transition, 'write_to_buffer', char_map, 0) )

  def test_write_to_buffer_with_index_non_zero(self):
    char_map = btl_desc_char_map()
    cmd = btl_desc_state_command('yield', 't_cheese')
    transition = btl_desc_state_transition('s_kiwi', 'c_equal', [ cmd ])
    
    self.assert_code_equal('''
elif c in {61}:
  new_state = s_kiwi
  tokens.append(self.make_token(t_cheese, self.buffer_value(), self.position)
''', self.call_buf_func(transition, 'write_to_buffer', char_map, 1) )
    
if __name__ == '__main__':
  unit_test.main()

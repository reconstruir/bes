 #!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.btl.btl_lexer_desc_state_command import btl_lexer_desc_state_command
from bes.btl.btl_lexer_desc_state_transition import btl_lexer_desc_state_transition
from bes.btl.btl_error import btl_error
from bes.btl.btl_lexer_desc_char_map import btl_lexer_desc_char_map
from bes.testing.unit_test import unit_test
from bes.text.tree_text_parser import _text_node_data

from _test_lexer_desc_mixin import _test_lexer_desc_mixin

class test_btl_lexer_desc_state_transition(_test_lexer_desc_mixin, unit_test):

  def test_generate_code(self):
    char_map = btl_lexer_desc_char_map()
    cmd = btl_lexer_desc_state_command('emit', 't_cheese', {})
    transition = btl_lexer_desc_state_transition('s_kiwi', 'c_equal', [ cmd ])
    
    self.assert_code_equal('''
if self.char_in(c, 'c_equal'):
  new_state = 's_kiwi'
  tokens.append(self.make_token('t_cheese', args = {}))
''', self.call_buf_func(transition, 'generate_code', char_map, 0, 2) )

  def test_generate_code_with_index_non_zero(self):
    char_map = btl_lexer_desc_char_map()
    cmd = btl_lexer_desc_state_command('emit', 't_cheese', {})
    transition = btl_lexer_desc_state_transition('s_kiwi', 'c_equal', [ cmd ])
    
    self.assert_code_equal('''
elif self.char_in(c, 'c_equal'):
  new_state = 's_kiwi'
  tokens.append(self.make_token('t_cheese', args = {}))
''', self.call_buf_func(transition, 'generate_code', char_map, 1, 2) )
    
if __name__ == '__main__':
  unit_test.main()

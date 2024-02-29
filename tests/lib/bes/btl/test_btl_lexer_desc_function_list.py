 #!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.btl.btl_lexer_desc_function_list import btl_lexer_desc_function_list
from bes.testing.unit_test import unit_test

from _test_simple_lexer_mixin import _test_simple_lexer_mixin

class test_btl_lexer_desc_function_list(_test_simple_lexer_mixin, unit_test):

  def test_parse_node(self):
    functions_node = self._simple_lexer_desc_tree_section('functions')

#    d = btl_lexer_desc_function_list.parse_node(functions_node).to_dict()
#    import pprint
#    print(pprint.pformat(d))
    
    self.assertEqual( {
      'f_handle_eos': {
        'args': ['token_name'],
        'commands': [
          {'action': '${token_name}',
           'args': {},
           'name': 'emit'},
          {'action': 'reset',
           'args': {},
           'name': 'buffer'},
          {'action': 't_done',
           'args': {},
           'name': 'emit'}],
        'name': 'f_handle_eos'
      }
    }, btl_lexer_desc_function_list.parse_node(functions_node).to_dict() )
    
  def xtest_generate_code(self):
    char_map = btl_lexer_desc_char_map()
    cmd = btl_lexer_desc_function_command('emit', 't_cheese', {})
    transition = btl_lexer_desc_function('s_kiwi', 'c_equal', [ cmd ])
    
    self.assert_python_code_text_equal('''
if self.char_in(c, 'c_equal', context):
  new_state_name = 's_kiwi'
  tokens.append(self.make_token(context, 't_cheese', args = {}))
''', self.call_function_with_buf(transition, 'generate_code', [], char_map, 0, 2) )

  def xtest_generate_code_with_index_non_zero(self):
    char_map = btl_lexer_desc_char_map()
    cmd = btl_lexer_desc_function_command('emit', 't_cheese', {})
    transition = btl_lexer_desc_function('s_kiwi', 'c_equal', [ cmd ])
    
    self.assert_python_code_text_equal('''
elif self.char_in(c, 'c_equal', context):
  new_state_name = 's_kiwi'
  tokens.append(self.make_token(context, 't_cheese', args = {}))
''', self.call_function_with_buf(transition, 'generate_code', [], char_map, 1, 2) )
    
if __name__ == '__main__':
  unit_test.main()

 #!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.btl.btl_lexer_desc_state_transition_command_list import btl_lexer_desc_state_transition_command_list
from bes.btl.btl_lexer_desc_function import btl_lexer_desc_function
from bes.btl.btl_error import btl_error
from bes.btl.btl_lexer_desc_char_map import btl_lexer_desc_char_map
from bes.testing.unit_test import unit_test

from _test_simple_lexer_mixin import _test_simple_lexer_mixin

class test_btl_lexer_desc_function(_test_simple_lexer_mixin, unit_test):

  def test__is_valid_identifier(self):
    f = btl_lexer_desc_function._is_valid_identifier
    self.assertEqual( True, f('k') )
    self.assertEqual( True, f('_') )
    self.assertEqual( True, f('kiwi') )
    self.assertEqual( True, f('_kiwi') )
    self.assertEqual( True, f('kiwi_green') )
    self.assertEqual( True, f('kiwi2') )
    self.assertEqual( False, f('2kiwi') )
    self.assertEqual( False, f('kiw!') )
    self.assertEqual( False, f('ki wi') )

  def test__parse_declaration(self):
    f = btl_lexer_desc_function._parse_declaration
    self.assertEqual( ( 'kiwi', ( 'color', 'taste' ) ), f('kiwi(color, taste)') )
    self.assertEqual( ( 'kiwi2', ( 'color2', 'taste2' ) ), f('kiwi2(color2, taste2)') )
    self.assertEqual( ( 'kiwi', ( 'color', 'taste' ) ), f('kiwi(   color,   taste   )') )
    self.assertEqual( ( 'kiwi', ( 'color', 'taste' ) ), f('kiwi   (color, taste)') )
    self.assertEqual( ( 'kiwi', ( 'color', 'taste' ) ), f(' kiwi(color, taste)') )
    self.assertEqual( ( 'kiwi', ( 'color', 'taste' ) ), f('kiwi(color, taste) ') )
    self.assertEqual( ( 'kiwi', () ), f('kiwi()') )
    self.assertEqual( None, f('kiwi') )

  def test_parse_node(self):
    functions_node = self._simple_lexer_desc_tree_section('functions')
    lexer_node = functions_node.children[0]
    self.assertEqual( {
      'args': ['token_name'],
      'commands': [
        {
          'action': '${token_name}',
          'args': {},
          'name': 'emit'
        },
        {
          'action': 'reset',
          'args': {}, 'name':
          'buffer'
        },
        {
          'action': 't_done',
          'args': {},
          'name': 'emit'
        },
      ],
      'name': 'f_handle_eos',
    }, btl_lexer_desc_function.parse_node(lexer_node).to_dict() )

  def test_generate_code(self):
    functions_node = self._simple_lexer_desc_tree_section('functions')
    lexer_node = functions_node.children[0]
    function = btl_lexer_desc_function.parse_node(lexer_node)

    self.assert_python_code_text_equal('''
class _function_f_handle_eos(btl_function_base):
  def call(self, context, tokens, token_name):
    tokens.append(self.make_token(context, token_name, args = {}))
    context.buffer_reset()
    tokens.append(self.make_token(context, 't_done', args = {}))
''', self.call_function_with_buf(function, 'generate_code', []) )
    
if __name__ == '__main__':
  unit_test.main()

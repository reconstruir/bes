#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
from bes.system.check import check
from bes.testing.unit_test import unit_test

from bes.btl.btl_lexer_token import btl_lexer_token
from bes.btl.btl_document_base import btl_document_base

from _test_simple_lexer import _test_simple_lexer
from _test_simple_parser import _test_simple_parser

class _test_document_error(Exception):
  def __init__(self, message = None):
    super().__init__()

    self.message = message

  def __str__(self):
    return self.message or ''

class _test_document(btl_document_base):

  @classmethod
  #@abstractmethod
  def lexer_class(clazz):
    return _test_simple_lexer

  @classmethod
  #@abstractmethod
  def parser_class(clazz):
    return _test_simple_parser

  @classmethod
  #@abstractmethod
  def exception_class(clazz):
    return _test_document_error

  #@abstractmethod
  def determine_insert_index(self, parent_node, child_node, new_tokens):
    insert_index = self.default_insert_index(parent_node, self._tokens)
    self._log.log_d(f'determine_insert_index: insert_index={insert_index} parent_node=\n{parent_node}\n new_tokens=\n{new_tokens.to_debug_str()}', multi_line = True)
    skipped_insert_index = self.tokens.skip_index_by_name(insert_index, 'right', 't_line_break', '*')
    self._log.log_d(f'determine_insert_index: skipped_insert_index={skipped_insert_index}')
    return skipped_insert_index

  def get_value(self, key):
    check.check_string(key)

    kv_node = self._find_key_value_node(key, raise_error = True)
    return kv_node.children[1].token.value
    
  def set_value(self, key, value):
    check.check_string(key)
    check.check_string(value)

    self._log.log_d(f'set_value: key="{key}" value="{value}"')
    self._log.log_d(f'set_value: tokens before:\n{self._tokens.to_debug_str()}', multi_line = True)
    self._log.log_d(f'set_value: root_node before:\n{str(self._root_node)}', multi_line = True)
    kv_node = self._find_key_value_node(key, raise_error = False)
    if not kv_node:
      self.add_value(key, value)
      kv_node = self._find_key_value_node(key, raise_error = True)
    self._key_value_node_modify_value(kv_node, value)
    self._update_text()
    self._log.log_d(f'set_value: tokens after:\n{self._tokens.to_debug_str()}', multi_line = True)
    self._log.log_d(f'set_value: root_node after:\n{str(self._root_node)}', multi_line = True)

  def add_value(self, key, value):
    check.check_string(key)
    check.check_string(value)

    return self.add_node_from_text(self.root_node,
                                   f'{key}={value}',
                                   ( 'n_key_value', ))

  def remove_value(self, key):
    check.check_string(key)

  def _find_key_value_node(self, key, raise_error = True):
    key_value_node =  self.root_node.find_grandchild_by_token('n_key_value',
                                                              'n_key',
                                                              't_key',
                                                              key)
    if not key_value_node and raise_error:
      raise self._exception_class(f'key value not found: "{key}"')
    return key_value_node

  def _key_value_node_modify_value(self, key_value_node, new_value):
    token = key_value_node.children[1].token
    token.replace_value(new_value)
    
class test_btl_document_base(unit_test):

  def test_insert_one_token(self):
    doc = _test_document('''
name=apple
color=red
''')

    self.assert_python_code_text_equal( '''
0: t_line_break:[NL]:p=1,1:h=h_line_break:i=0
1: t_key:name:p=2,1:i=1
2: t_key_value_delimiter:=:p=2,5:i=2
3: t_value:apple:p=2,6:i=3
4: t_line_break:[NL]:p=2,11:h=h_line_break:i=4
5: t_key:color:p=3,1:i=5
6: t_key_value_delimiter:=:p=3,6:i=6
7: t_value:red:p=3,7:i=7
8: t_line_break:[NL]:p=3,10:h=h_line_break:i=8
''', doc.tokens.to_debug_str() )

    new_token = btl_lexer_token('t_line_break', '\n', ( 1, 1 ), 'h_line_break', 666)
    doc.insert_token(5, new_token)

    self.assertMultiLineEqual('''
name=apple

color=red
''', doc.text )
    
    self.assert_python_code_text_equal( '''
0: t_line_break:[NL]:p=1,1:h=h_line_break:i=0
1: t_key:name:p=2,1:i=1
2: t_key_value_delimiter:=:p=2,5:i=2
3: t_value:apple:p=2,6:i=3
4: t_line_break:[NL]:p=2,11:h=h_line_break:i=4
5: t_line_break:[NL]:p=3,1:h=h_line_break:i=5
6: t_key:color:p=4,1:i=6
7: t_key_value_delimiter:=:p=4,6:i=7
8: t_value:red:p=4,7:i=8
9: t_line_break:[NL]:p=4,10:h=h_line_break:i=9
''', doc.tokens.to_debug_str() )

  def test_insert_many_tokens(self):
    doc = _test_document('''
name=apple
color=red
''')

    self.assert_python_code_text_equal( '''
0: t_line_break:[NL]:p=1,1:h=h_line_break:i=0
1: t_key:name:p=2,1:i=1
2: t_key_value_delimiter:=:p=2,5:i=2
3: t_value:apple:p=2,6:i=3
4: t_line_break:[NL]:p=2,11:h=h_line_break:i=4
5: t_key:color:p=3,1:i=5
6: t_key_value_delimiter:=:p=3,6:i=6
7: t_value:red:p=3,7:i=7
8: t_line_break:[NL]:p=3,10:h=h_line_break:i=8
''', doc.tokens.to_debug_str() )

    new_tokens = doc.lexer.lex_all('''
price=cheap
''')
    new_tokens.pop(-1)    

    self.assert_python_code_text_equal( '''
0: t_line_break:[NL]:p=1,1:h=h_line_break
1: t_key:price:p=2,1
2: t_key_value_delimiter:=:p=2,6
3: t_value:cheap:p=2,7
4: t_line_break:[NL]:p=2,12:h=h_line_break
''', new_tokens.to_debug_str() )

    doc.insert_tokens(5, new_tokens)
    
    self.assertMultiLineEqual('''
name=apple

price=cheap
color=red
''', doc.text )
  
    self.assert_python_code_text_equal( '''
 0: t_line_break:[NL]:p=1,1:h=h_line_break:i=0
 1: t_key:name:p=2,1:i=1
 2: t_key_value_delimiter:=:p=2,5:i=2
 3: t_value:apple:p=2,6:i=3
 4: t_line_break:[NL]:p=2,11:h=h_line_break:i=4
 5: t_line_break:[NL]:p=3,1:h=h_line_break:i=5
 6: t_key:price:p=4,1:i=6
 7: t_key_value_delimiter:=:p=4,6:i=7
 8: t_value:cheap:p=4,7:i=8
 9: t_line_break:[NL]:p=4,12:h=h_line_break:i=9
10: t_key:color:p=5,1:i=10
11: t_key_value_delimiter:=:p=5,6:i=11
12: t_value:red:p=5,7:i=12
13: t_line_break:[NL]:p=5,10:h=h_line_break:i=13
''', doc.tokens.to_debug_str() )
    
  def test_insert_many_tokens_empty_doc(self):
    doc = _test_document('')

    self.assert_python_code_text_equal( '''
''', doc.tokens.to_debug_str() )

    new_tokens = doc.lexer.lex_all('''
price=cheap
''')
    new_tokens.pop(-1)    

    self.assert_python_code_text_equal( '''
0: t_line_break:[NL]:p=1,1:h=h_line_break
1: t_key:price:p=2,1
2: t_key_value_delimiter:=:p=2,6
3: t_value:cheap:p=2,7
4: t_line_break:[NL]:p=2,12:h=h_line_break
''', new_tokens.to_debug_str() )

    doc.insert_tokens(0, new_tokens)
    
    self.assertMultiLineEqual('''
price=cheap
''', doc.text )

    self.assert_python_code_text_equal( '''
0: t_line_break:[NL]:p=1,1:h=h_line_break:i=0
1: t_key:price:p=2,1:i=1
2: t_key_value_delimiter:=:p=2,6:i=2
3: t_value:cheap:p=2,7:i=3
4: t_line_break:[NL]:p=2,12:h=h_line_break:i=4
''', doc.tokens.to_debug_str() )

  def test_add_line_break(self):
    doc = _test_document('''
name=vieux
smell=stink
''')
    doc.add_line_break(2)
    self.assert_python_code_text_equal( '''
name=vieux

smell=stink
''', doc.text )

  def test_add_line_break_with_count(self):
    doc = _test_document('''
name=vieux
smell=stink
''')
    doc.add_line_break(2, count = 2)
    self.assert_python_code_text_equal( '''
name=vieux


smell=stink
''', doc.text )

  def test_save_file(self):
    doc = _test_document()
    doc.set_value('name', 'apple')
    doc.set_value('color', 'red')
    tmp = self.make_temp_file(suffix = '.config', non_existent = True)
    doc.save_file(tmp)

    self.assert_text_file_equal('''
name=apple
color=red
''', tmp, codec = 'utf-8', strip = True, native_line_breaks = True)

  def test_load_file(self):
    text = '''
name=apple
color=red
'''    
    tmp = self.make_temp_file(suffix = '.config', content = text)
    doc = _test_document.load_file(tmp)
    self.assertMultiLineEqual('''
name=apple
color=red
''', doc.text )
    
  def test_get_value(self):
    doc = _test_document('''
name=apple
color=red
''')
    self.assertEqual( 'apple', doc.get_value('name') )

  def test_add_value(self):
    doc = _test_document('''
name=apple
color=red
''')
    doc.add_value('price', 'cheap')
    self.assertMultiLineEqual('''
name=apple
color=red
price=cheap
''', doc.text )

  def test_add_value_with_line_breaks(self):
    doc = _test_document('''
name=apple
color=red


''')
    doc.add_value('price', 'cheap')
    self.assertMultiLineEqual('''
name=apple
color=red



price=cheap''', doc.text )
    
  def test_set_value(self):
    doc = _test_document('''
name=apple
color=red
''')
    doc.set_value('name', 'kiwi')
    self.assertMultiLineEqual('''
name=kiwi
color=red
''', doc.text )

  def test_set_value(self):
    doc = _test_document('''
name=apple
color=red
''')
    doc.set_value('price', 'cheap')
    self.assertMultiLineEqual('''
name=apple
color=red
price=cheap
''', doc.text )
    
if __name__ == '__main__':
  unit_test.main()

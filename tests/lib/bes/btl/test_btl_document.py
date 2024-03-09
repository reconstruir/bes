#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test

from bes.btl.btl_lexer_token import btl_lexer_token
from bes.btl.btl_document import btl_document

from _test_simple_lexer import _test_simple_lexer
from _test_simple_parser import _test_simple_parser

class _test_document(btl_document):

  @classmethod
  #@abstractmethod
  def lexer_class(clazz):
    return _test_simple_lexer

  @classmethod
  #@abstractmethod
  def parser_class(clazz):
    return _test_simple_parser

class test_btl_document(unit_test):

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
9: t_done::h=h_done:i=9
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
10: t_done::h=h_done:i=10
''', doc.tokens.to_debug_str() )
    
if __name__ == '__main__':
  unit_test.main()

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
    text = '''
name=vieux
smell=stink
'''
    doc = _test_document(text)
    self.assert_python_code_text_equal( text, doc.text )
    expected = '''
name=vieux

smell=stink
'''
    doc.add_line_break(2)
    self.assert_python_code_text_equal( expected, doc.text )

  def test_add_line_break_with_count(self):
    text = '''
name=vieux
smell=stink
'''
    doc = _test_document(text)
    self.assert_python_code_text_equal( text, doc.text )
    expected = '''
name=vieux


smell=stink
'''
    doc.add_line_break(2, count = 2)
    self.assert_python_code_text_equal( expected, doc.text )

if __name__ == '__main__':
  unit_test.main()

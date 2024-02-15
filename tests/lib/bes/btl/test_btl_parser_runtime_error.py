#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test

from bes.btl.btl_lexer_token import btl_lexer_token
from bes.btl.btl_parser_context import btl_parser_context
from bes.btl.btl_parser_runtime_error import btl_parser_runtime_error

from _test_simple_lexer import _test_simple_lexer
from _test_simple_parser import _test_simple_parser

class test_btl_parser_runtime_error(unit_test):

  def test_make_error_text(self):
    text = '''
; this is my config file.  there are many config files but this is mine

[treats]
name=ice cream
    
; fruit
[fruit]
name=
    
; cheese
name=manchego
taste=awesome

; wine
name=syrah
taste=earthy
'''
    position = ( 9, 6 )
    token = btl_lexer_token('t_fruit', 'kiwi', position)
    lexer = _test_simple_lexer()
    parser = _test_simple_parser(lexer)
    context = btl_parser_context(parser, 'tag', text, '<unit_test>')
    context.position = position
    class _text_runtime_error(btl_parser_runtime_error):
      pass
    
    with self.assertRaises(_text_runtime_error) as ctx:
      raise _text_runtime_error(token, context, 'borken')
    expected = '''\
<unit_test> line 9 column 6
borken
 5|name=ice cream
 6|    
 7|; fruit
 8|[fruit]
 9|name=
        ^^^ borken
10|    
11|; cheese
12|name=manchego
13|taste=awesome
14|\
'''
    actual = str(ctx.exception)
    self.assertMultiLineEqual( expected, actual )
    
if __name__ == '__main__':
  unit_test.main()

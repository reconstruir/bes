#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.btl.btl_parser_context import btl_parser_context
from bes.btl.btl_parser_options import btl_parser_options
from bes.btl.btl_lexer_options import btl_lexer_options

from _test_simple_lexer import _test_simple_lexer
from _test_simple_parser import _test_simple_parser

from bes.testing.unit_test import unit_test

class test_btl_parser_context(unit_test):

  def test_make_error_text(self):
    text = '''
[fruit]
name=
[cheese]
name=brie
'''
    expected = '''
[fruit]
name=
     ^
[cheese]
name=brie'''
    l = _test_simple_lexer()
    p = _test_simple_parser(l)
    lexer_options = btl_lexer_options(source = '<unit_test>')
    parser_options = btl_parser_options(lexer_options = lexer_options)
    c = btl_parser_context(p, 'tag', text, parser_options)
    self.assertMultiLineEqual( '<unit_test>', c.source )
    
if __name__ == '__main__':
  unit_test.main()

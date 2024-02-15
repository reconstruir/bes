#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.btl.btl_lexer_context import btl_lexer_context
from bes.btl.btl_lexer_token import btl_lexer_token

from _test_simple_lexer import _test_simple_lexer

from bes.testing.unit_test import unit_test

class test_btl_lexer_context(unit_test):

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
    c = btl_lexer_context(_test_simple_lexer(), 'tag', text, '<unit_test>', None)
    t = btl_lexer_token('t_kiwi', value = '', position = ( 3, 6 ))
#    self.assertMultiLineEqual( expected, c.make_error_text(t) )
    
if __name__ == '__main__':
  unit_test.main()

#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.btl.btl_lexer_token_list import btl_lexer_token_list
from bes.btl.btl_lexer_token import btl_lexer_token
from bes.btl.btl_error import btl_error
from bes.testing.unit_test import unit_test

from _test_desc_mixin import _test_desc_mixin

class test_btl_lexer_token_list(_test_desc_mixin, unit_test):

  def test_append(self):
    l = btl_lexer_token_list()
    l.append(( 'fruit', 'kiwi', ( 1, 1 ), None ))
    l.append(( 'color', 'red', ( 10, 1 ), None))
    self.assert_json_equal( '''
[
  {
    "name": "fruit",
    "value": "kiwi",
    "position": "1,1"
   },
   {
     "name": "color",
     "value": "red",
     "position": "10,1"
   }
]    
''', l.to_json() )

  def test_prepend(self):
    l = btl_lexer_token_list()
    l.append(( 'fruit', 'kiwi', ( 1, 1 ), None))
    l.prepend(( 'color', 'red', ( 10, 1 ), None))
    self.assert_json_equal( '''
[
  {
    "name": "color",
    "value": "red",
    "position": "10,1"
  },
  {
    "name": "fruit",
    "value": "kiwi",
    "position": "1,1"
  }
]
''', l.to_json() )
    
if __name__ == '__main__':
  unit_test.main()

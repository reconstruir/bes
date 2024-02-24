#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.btl.btl_lexer_token import btl_lexer_token
from bes.btl.btl_error import btl_error
from bes.testing.unit_test import unit_test

from _test_simple_lexer_mixin import _test_simple_lexer_mixin

class test_btl_lexer_token(_test_simple_lexer_mixin, unit_test):

  def test_to_json(self):
    self.assert_json_equal( '''
{
  "name": "fruit",
  "value": "kiwi",
  "position": "1,1", 
  "type_hint": null,
  "index": null
}
''', btl_lexer_token( 'fruit', 'kiwi', ( 1, 1 ), None).to_json() )

    self.assert_json_equal( '''
{
  "name": "color",
  "value": "red",
  "position": "10,1", 
  "type_hint": "h_color",
  "index": null
}
''', btl_lexer_token( 'color', 'red', ( 10, 1 ), 'h_color').to_json() )

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
    token = btl_lexer_token('t_fruit', 'kiwi', ( 9, 6 ))
    self.assertEqual('''\
 5|name=ice cream
 6|    
 7|; fruit
 8|[fruit]
 9|name=
        ^^^ unexpected token foo bar
10|    
11|; cheese
12|name=manchego
13|taste=awesome
14|\
'''
, token.make_error_text(text, 'unexpected token foo bar') )

  def test_parse_str(self):
    self.assertEqual( ( 'fruit', 'kiwi', ( 1, 1 ), None, None ),
                      btl_lexer_token.parse_str('fruit:kiwi:p=1,1') )
    
if __name__ == '__main__':
  unit_test.main()

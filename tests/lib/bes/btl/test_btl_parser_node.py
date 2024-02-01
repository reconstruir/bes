#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.btl.btl_parser_node import btl_parser_node
from bes.btl.btl_error import btl_error
from bes.testing.unit_test import unit_test

from _test_lexer_desc_mixin import _test_lexer_desc_mixin

class test_btl_parser_node(_test_lexer_desc_mixin, unit_test):

  def test_to_json(self):
    self.assert_json_equal( '''
{
  "name": "fruit",
  "value": "kiwi",
  "position": "1,1", 
  "type_hint": null
}
''', btl_parser_node( 'fruit', 'kiwi', ( 1, 1 ), None).to_json() )

    self.assert_json_equal( '''
{
  "name": "color",
  "value": "red",
  "position": "10,1", 
  "type_hint": "h_color"
}
''', btl_parser_node( 'color', 'red', ( 10, 1 ), 'h_color').to_json() )
    
if __name__ == '__main__':
  unit_test.main()

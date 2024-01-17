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
    l.append(( 'color', 'red', ( 10, 1 ), 'h_color'))
    self.assert_json_equal( '''
[
  {
    "name": "fruit",
    "value": "kiwi",
    "position": "1,1",
    "type_hint": null
   },
   {
     "name": "color",
     "value": "red",
     "position": "10,1", 
     "type_hint": "h_color"
   }
]    
''', l.to_json() )

  def test_prepend(self):
    l = btl_lexer_token_list()
    l.append(( 'fruit', 'kiwi', ( 1, 1 ), None))
    l.prepend(( 'color', 'red', ( 10, 1 ), 'h_color'))
    self.assert_json_equal( '''
[
  {
    "name": "color",
    "value": "red",
    "position": "10,1",
    "type_hint": "h_color"
  },
  {
    "name": "fruit",
    "value": "kiwi",
    "position": "1,1", 
    "type_hint": null
  }
]
''', l.to_json() )

  def test_parse_json(self):
    tokens = btl_lexer_token_list.parse_json(self._JSON_TEXT)
    self.assert_json_equal( self._JSON_TEXT, tokens.to_json() )

  def test_to_ordered_dict(self):
    tokens = btl_lexer_token_list.parse_json(self._JSON_TEXT)
    d = tokens.to_ordered_dict()
    self.assertEqual( 3, len(d) )

    if self.DEBUG:
      for line_number, tokens in d.items():
        print(f'{line_number}:')
        for token in tokens:
          print(f'  {token}')

    self.assert_json_equal( '''
[
]
''', d[1].to_json() )

    self.assert_json_equal( '''
[
  {
    "name": "t_key",
    "value": "fruit",
    "position": "1,2",
    "type_hint": null
  },
  {
    "name": "t_equal",
    "value": "=",
    "position": "6,2",
    "type_hint": null
  },
  {
    "name": "t_value",
    "value": "kiwi",
    "position": "7,2",
    "type_hint": null
  }
]
''', d[2].to_json() )

    self.assert_json_equal( '''
[
  {
    "name": "t_key",
    "value": "color",
    "position": "1,3",
    "type_hint": null
  },
  {
    "name": "t_equal",
    "value": "=",
    "position": "6,3",
    "type_hint": null
  },
  {
    "name": "t_value",
    "value": "green",
    "position": "7,3",
    "type_hint": null
  }
]
''', d[3].to_json() )
    
  _JSON_TEXT = '''
[
  {
    "name": "t_line_break", 
    "value": "\\n", 
    "position": "1,1", 
    "type_hint": "h_line_break"
  }, 
  {
    "name": "t_key", 
    "value": "fruit", 
    "position": "1,2", 
    "type_hint": null
  }, 
  {
    "name": "t_equal", 
    "value": "=", 
    "position": "6,2", 
    "type_hint": null
  }, 
  {
    "name": "t_value", 
    "value": "kiwi", 
    "position": "7,2", 
    "type_hint": null
  }, 
  {
    "name": "t_line_break", 
    "value": "\\n", 
    "position": "11,2", 
    "type_hint": "h_line_break"
  }, 
  {
    "name": "t_key", 
    "value": "color", 
    "position": "1,3", 
    "type_hint": null
  }, 
  {
    "name": "t_equal", 
    "value": "=", 
    "position": "6,3", 
    "type_hint": null
  }, 
  {
    "name": "t_value", 
    "value": "green", 
    "position": "7,3", 
    "type_hint": null
  }, 
  {
    "name": "t_line_break", 
    "value": "\\n", 
    "position": "12,3", 
    "type_hint": "h_line_break"
  }, 
  {
    "name": "t_done", 
    "value": null, 
    "position": "", 
    "type_hint": "h_done"
  }
]
'''
    
if __name__ == '__main__':
  unit_test.main()

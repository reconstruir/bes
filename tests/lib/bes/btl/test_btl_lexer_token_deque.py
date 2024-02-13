#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.btl.btl_lexer_token_deque import btl_lexer_token_deque
from bes.btl.btl_lexer_token import btl_lexer_token
from bes.btl.btl_error import btl_error
from bes.testing.unit_test import unit_test

from _test_simple_lexer_mixin import _test_simple_lexer_mixin

class test_btl_lexer_token_deque(_test_simple_lexer_mixin, unit_test):

  def test_append(self):
    l = btl_lexer_token_deque()
    l.append(( 'fruit', 'kiwi', ( 1, 1 ), None, None ))
    l.append(( 'color', 'red', ( 10, 1 ), 'h_color', None ))
    self.assert_json_equal( '''
[
  {
    "name": "fruit",
    "value": "kiwi",
    "position": "1,1",
    "type_hint": null,
    "index": null
   },
   {
     "name": "color",
     "value": "red",
     "position": "10,1", 
     "type_hint": "h_color",
     "index": null
   }
]    
''', l.to_json() )

  def test_prepend(self):
    l = btl_lexer_token_deque()
    l.append(( 'fruit', 'kiwi', ( 1, 1 ), None, None))
    l.prepend(( 'color', 'red', ( 10, 1 ), 'h_color', None))
    self.assert_json_equal( '''
[
  {
    "name": "color",
    "value": "red",
    "position": "10,1",
    "type_hint": "h_color",
    "index": null
  },
  {
    "name": "fruit",
    "value": "kiwi",
    "position": "1,1", 
    "type_hint": null,
    "index": null
  }
]
''', l.to_json() )

  def test_parse_json(self):
    tokens = btl_lexer_token_deque.parse_json(self._JSON_TEXT)
    self.assert_json_equal( self._JSON_TEXT, tokens.to_json() )

  def test_to_line_break_ordered_dict(self):
    tokens = btl_lexer_token_deque.parse_json(self._JSON_TEXT)
    d = tokens.to_line_break_ordered_dict()
    self.assertEqual( 3, len(d) )

    if self.DEBUG:
      for line_number, tokens in d.items():
        print(f'{line_number}:')
        for token in tokens:
          print(f'  {token}')

    self.assert_json_equal( '''
[
  {
    "name": "t_line_break",
    "value": "\\n",
    "position": "1,1",
    "type_hint": "h_line_break",
    "index": null
  }
]
''', d[1].to_json() )

    self.assert_json_equal( '''
[
  {
    "name": "t_key",
    "value": "fruit",
    "position": "1,2",
    "type_hint": null,
    "index": null
  },
  {
    "name": "t_key_value_delimiter",
    "value": "=",
    "position": "6,2",
    "type_hint": null,
    "index": null
  },
  {
    "name": "t_value",
    "value": "kiwi",
    "position": "7,2",
    "type_hint": null,
    "index": null
  },
  {
    "name": "t_line_break",
    "value": "\\n",
    "position": "11,2",
    "type_hint": "h_line_break",
    "index": null
  }
]
''', d[2].to_json() )

    self.assert_json_equal( '''
[
  {
    "name": "t_key",
    "value": "color",
    "position": "1,3",
    "type_hint": null,
    "index": null
  },
  {
    "name": "t_key_value_delimiter",
    "value": "=",
    "position": "6,3",
    "type_hint": null,
    "index": null
  },
  {
    "name": "t_value",
    "value": "green",
    "position": "7,3",
    "type_hint": null,
    "index": null
  },
  {
    "name": "t_line_break",
    "value": "\\n",
    "position": "12,3",
    "type_hint": "h_line_break",
    "index": null
  }
]
''', d[3].to_json() )

  def test_modify_value_shrinks(self):
    l = btl_lexer_token_deque()
    l.append(( 'fruit', 'kiwi', ( 1, 1 ), None, None ))
    l.append(( 'color', 'red', ( 10, 1 ), 'h_color', None ))
    l.modify_value('fruit', 'k')
    self.assert_json_equal( '''
[
  {
    "name": "fruit",
    "value": "k",
    "position": "1,1",
    "type_hint": null,
    "index": null
   },
   {
    "name": "color",
    "value": "red",
    "position": "7,1", 
    "type_hint": "h_color",
    "index": null
   }
]    
''', l.to_json() )
    
  def test_modify_value_grows(self):
    l = btl_lexer_token_deque()
    l.append(( 'fruit', 'kiwi', ( 1, 1 ), None, None ))
    l.append(( 'color', 'red', ( 10, 1 ), 'h_color', None))
    l.modify_value('fruit', 'watermelon')
    self.assert_json_equal( '''
[
  {
    "name": "fruit",
    "value": "watermelon",
    "position": "1,1",
    "type_hint": null,
    "index": null
   },
   {
    "name": "color",
    "value": "red",
    "position": "16,1", 
    "type_hint": "h_color",
    "index": null
   }
]    
''', l.to_json() )

  def test_shift_y(self):
    l = btl_lexer_token_deque()
    l.append(( 'fruit', 'kiwi', ( 1, 1 ), None, None ))
    l.append(( 'color', 'red', ( 10, 1 ), 'h_color', None))
    l.shift_y(1)
    self.assert_json_equal( '''
[
  {
    "name": "fruit",
    "value": "kiwi",
    "position": "1,2",
    "type_hint": null,
    "index": null
   },
   {
    "name": "color",
    "value": "red",
    "position": "10,2", 
    "type_hint": "h_color",
    "index": null
   }
]    
''', l.to_json() )

  def test___getitem__(self):
    d = btl_lexer_token_deque()
    t0 = btl_lexer_token( 'fruit', 'kiwi', ( 1, 1 ), None, None )
    t1 = btl_lexer_token( 'color', 'red', ( 10, 1 ), 'h_color', None )
    t2 = btl_lexer_token( 'flavor', 'tart', ( 20, 1 ), None, None )
    d.append(t0)
    d.append(t1)
    d.append(t2)
    self.assertEqual( t0, d[0] )
    self.assertEqual( t1, d[1] )
    self.assertEqual( t2, d[2] )
    
  _JSON_TEXT = '''
[
  {
    "name": "t_line_break", 
    "value": "\\n", 
    "position": "1,1", 
    "type_hint": "h_line_break",
    "index": null
  }, 
  {
    "name": "t_key", 
    "value": "fruit", 
    "position": "1,2", 
    "type_hint": null,
    "index": null
  }, 
  {
    "name": "t_key_value_delimiter", 
    "value": "=", 
    "position": "6,2", 
    "type_hint": null,
    "index": null
  }, 
  {
    "name": "t_value", 
    "value": "kiwi", 
    "position": "7,2", 
    "type_hint": null,
    "index": null
  }, 
  {
    "name": "t_line_break", 
    "value": "\\n", 
    "position": "11,2", 
    "type_hint": "h_line_break",
    "index": null
  }, 
  {
    "name": "t_key", 
    "value": "color", 
    "position": "1,3", 
    "type_hint": null,
    "index": null
  }, 
  {
    "name": "t_key_value_delimiter", 
    "value": "=", 
    "position": "6,3", 
    "type_hint": null,
    "index": null
  }, 
  {
    "name": "t_value", 
    "value": "green", 
    "position": "7,3", 
    "type_hint": null,
    "index": null
  }, 
  {
    "name": "t_line_break", 
    "value": "\\n", 
    "position": "12,3", 
    "type_hint": "h_line_break",
    "index": null
  }, 
  {
    "name": "t_done", 
    "value": null, 
    "position": "", 
    "type_hint": "h_done",
    "index": null
  }
]
'''
  
  def test_insert(self):
    l = btl_lexer_token_deque()
    l.append(( 'fruit', 'kiwi', ( 1, 1 ), None, None ))
    l.append(( 'color', 'red', ( 10, 1 ), 'h_color', None ))
    l.append(( 'flavor', 'tart', ( 1, 2 ), None, None ))
    l.insert(1, ( 'price', 'cheap', ( 1, 3 ), None, None ))
    self.assert_json_equal( '''
[
  {
    "name": "fruit",
    "value": "kiwi",
    "position": "1,1",
    "type_hint": null,
    "index": null
  },
  {
    "name": "price",
    "value": "cheap",
    "position": "1,3",
    "type_hint": null,
    "index": null
  },
  {
    "name": "color",
    "value": "red",
    "position": "10,1",
    "type_hint": "h_color",
    "index": null
  },
  {
    "name": "flavor",
    "value": "tart",
    "position": "1,2",
    "type_hint": null,
    "index": null
  }
]
''', l.to_json() )

  def test_insert_with_negative_index(self):
    l = btl_lexer_token_deque()
    l.append(( 'fruit', 'kiwi', ( 1, 1 ), None, None ))
    l.append(( 'color', 'red', ( 10, 1 ), 'h_color', None ))
    l.append(( 'flavor', 'tart', ( 1, 2 ), None, None ))
    l.insert(-1, ( 'price', 'cheap', ( 1, 3 ), None, None ))
    self.assert_json_equal( '''
[
  {
    "name": "fruit",
    "value": "kiwi",
    "position": "1,1",
    "type_hint": null,
    "index": null
  },
  {
    "name": "color",
    "value": "red",
    "position": "10,1",
    "type_hint": "h_color",
    "index": null
  },
  {
    "name": "flavor",
    "value": "tart",
    "position": "1,2",
    "type_hint": null,
    "index": null
  },
  {
    "name": "price",
    "value": "cheap",
    "position": "1,3",
    "type_hint": null,
    "index": null
  }
]
''', l.to_json() )

  def test_insert_with_empty_deque(self):
    l = btl_lexer_token_deque()
    l.insert(0, ( 'price', 'cheap', ( 1, 3 ), None, None ))
    self.assert_json_equal( '''
[
  {
    "name": "price",
    "value": "cheap",
    "position": "1,3",
    "type_hint": null,
    "index": null
  }
]
''', l.to_json() )
    
  
if __name__ == '__main__':
  unit_test.main()

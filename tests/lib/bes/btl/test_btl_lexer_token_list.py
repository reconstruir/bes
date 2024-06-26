#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.btl.btl_lexer_token_list import btl_lexer_token_list
from bes.btl.btl_lexer_token import btl_lexer_token
from bes.btl.btl_error import btl_error
from bes.testing.unit_test import unit_test

from _test_simple_lexer_mixin import _test_simple_lexer_mixin

class test_btl_lexer_token_list(_test_simple_lexer_mixin, unit_test):

  def test_append(self):
    l = btl_lexer_token_list()
    l.append(( 'fruit', 'kiwi', ( 1, 1 ), None, None ))
    l.append(( 'color', 'red', ( 1, 10 ), 'h_color', None ))
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
     "position": "1,10", 
     "type_hint": "h_color",
     "index": null
   }
]    
''', l.to_json() )

  def test_prepend(self):
    l = btl_lexer_token_list()
    l.append(( 'fruit', 'kiwi', ( 1, 1 ), None, None))
    l.prepend(( 'color', 'red', ( 1, 10 ), 'h_color', None))
    self.assert_json_equal( '''
[
  {
    "name": "color",
    "value": "red",
    "position": "1,10",
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
    tokens = btl_lexer_token_list.parse_json(self._JSON_TEXT)
    self.assert_json_equal( self._JSON_TEXT, tokens.to_json() )

  def test_to_line_break_ordered_dict(self):
    tokens = btl_lexer_token_list.parse_json(self._JSON_TEXT)
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
    "position": "2,1",
    "type_hint": null,
    "index": null
  },
  {
    "name": "t_key_value_delimiter",
    "value": "=",
    "position": "2,6",
    "type_hint": null,
    "index": null
  },
  {
    "name": "t_value",
    "value": "kiwi",
    "position": "2,7",
    "type_hint": null,
    "index": null
  },
  {
    "name": "t_line_break",
    "value": "\\n",
    "position": "2,11",
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
    "position": "3,1",
    "type_hint": null,
    "index": null
  },
  {
    "name": "t_key_value_delimiter",
    "value": "=",
    "position": "3,6",
    "type_hint": null,
    "index": null
  },
  {
    "name": "t_value",
    "value": "green",
    "position": "3,7",
    "type_hint": null,
    "index": null
  },
  {
    "name": "t_line_break",
    "value": "\\n",
    "position": "3,12",
    "type_hint": "h_line_break",
    "index": null
  }
]
''', d[3].to_json() )

  def test_modify_value_shrinks(self):
    l = btl_lexer_token_list()
    l.append(( 'fruit', 'kiwi', ( 1, 1 ), None, None ))
    l.append(( 'color', 'red', ( 1, 10 ), 'h_color', None ))
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
    "position": "1,7", 
    "type_hint": "h_color",
    "index": null
   }
]    
''', l.to_json() )
    
  def test_modify_value_grows(self):
    l = btl_lexer_token_list()
    l.append(( 'fruit', 'kiwi', ( 1, 1 ), None, None ))
    l.append(( 'color', 'red', ( 1, 10 ), 'h_color', None))
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
    "position": "1,16", 
    "type_hint": "h_color",
    "index": null
   }
]    
''', l.to_json() )

  def test_shift_vertical(self):
    l = btl_lexer_token_list()
    l.append(( 'fruit', 'kiwi', ( 1, 1 ), None, None ))
    l.append(( 'color', 'red', ( 1, 10 ), 'h_color', None))
    l.shift_vertical(1)
    self.assert_json_equal( '''
[
  {
    "name": "fruit",
    "value": "kiwi",
    "position": "2,1",
    "type_hint": null,
    "index": null
   },
   {
    "name": "color",
    "value": "red",
    "position": "2,10", 
    "type_hint": "h_color",
    "index": null
   }
]    
''', l.to_json() )

  def test___getitem__(self):
    d = btl_lexer_token_list()
    t0 = btl_lexer_token( 'fruit', 'kiwi', ( 1, 1 ), None, None )
    t1 = btl_lexer_token( 'color', 'red', ( 10, 1 ), 'h_color', None )
    t2 = btl_lexer_token( 'flavor', 'tart', ( 20, 1 ), None, None )
    d.append(t0)
    d.append(t1)
    d.append(t2)
    self.assertEqual( t0, d[0] )
    self.assertEqual( t1, d[1] )
    self.assertEqual( t2, d[2] )

  def test___setitem__(self):
    d = btl_lexer_token_list()
    t0 = btl_lexer_token( 'fruit', 'kiwi', ( 1, 1 ), None, None )
    t1 = btl_lexer_token( 'color', 'red', ( 10, 1 ), 'h_color', None )
    t2 = btl_lexer_token( 'flavor', 'tart', ( 20, 1 ), None, None )
    d.append(t0)
    d.append(t1)
    d.append(t2)
    self.assertEqual( t0, d[0] )
    self.assertEqual( t1, d[1] )
    self.assertEqual( t2, d[2] )
    new_token = btl_lexer_token( 'color', 'yellow', ( 10, 1 ), 'h_color', None )
    d[1] = new_token
    self.assertEqual( t0, d[0] )
    self.assertEqual( new_token, d[1] )
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
    "position": "2,1", 
    "type_hint": null,
    "index": null
  }, 
  {
    "name": "t_key_value_delimiter", 
    "value": "=", 
    "position": "2,6", 
    "type_hint": null,
    "index": null
  }, 
  {
    "name": "t_value", 
    "value": "kiwi", 
    "position": "2,7", 
    "type_hint": null,
    "index": null
  }, 
  {
    "name": "t_line_break", 
    "value": "\\n", 
    "position": "2,11", 
    "type_hint": "h_line_break",
    "index": null
  }, 
  {
    "name": "t_key", 
    "value": "color", 
    "position": "3,1", 
    "type_hint": null,
    "index": null
  }, 
  {
    "name": "t_key_value_delimiter", 
    "value": "=", 
    "position": "3,6", 
    "type_hint": null,
    "index": null
  }, 
  {
    "name": "t_value", 
    "value": "green", 
    "position": "3,7", 
    "type_hint": null,
    "index": null
  }, 
  {
    "name": "t_line_break", 
    "value": "\\n", 
    "position": "3,12", 
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
    l = btl_lexer_token_list()
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
    l = btl_lexer_token_list()
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
    l = btl_lexer_token_list()
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
    
  def test_replace_by_index(self):
    d = btl_lexer_token_list()
    t0 = btl_lexer_token( 'fruit', 'kiwi', ( 1, 1 ), None, None )
    t1 = btl_lexer_token( 'color', 'red', ( 10, 1 ), 'h_color', None )
    t2 = btl_lexer_token( 'flavor', 'tart', ( 20, 1 ), None, None )
    d.append(t0)
    d.append(t1)
    d.append(t2)
    self.assertEqual( t0, d[0] )
    self.assertEqual( t1, d[1] )
    self.assertEqual( t2, d[2] )
    new_token = btl_lexer_token( 'color', 'green', ( 10, 1 ), 'h_color', None )
    d.replace_by_index(1, new_token)
    self.assertEqual( t0, d[0] )
    self.assertEqual( new_token, d[1] )
    self.assertEqual( t2, d[2] )

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
    "value": "green",
    "position": "10,1",
    "type_hint": "h_color",
    "index": null
  },
  {
    "name": "flavor",
    "value": "tart",
    "position": "20,1",
    "type_hint": null,
    "index": null
  }
]
''', d.to_json() )

  def test_remove_by_index(self):
    d = btl_lexer_token_list()
    t0 = btl_lexer_token( 'fruit', 'kiwi', ( 1, 1 ), None, None )
    t1 = btl_lexer_token( 'color', 'red', ( 10, 1 ), 'h_color', None )
    t2 = btl_lexer_token( 'flavor', 'tart', ( 20, 1 ), None, None )
    d.append(t0)
    d.append(t1)
    d.append(t2)
    self.assertEqual( t0, d[0] )
    self.assertEqual( t1, d[1] )
    self.assertEqual( t2, d[2] )
    self.assertEqual( 3, len(d) )
    removed_token = d.remove_by_index(1)
    self.assertEqual( 2, len(d) )
    self.assertEqual( t1, removed_token )
    self.assertEqual( t0, d[0] )
    self.assertEqual( t2, d[1] )

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
    "name": "flavor",
    "value": "tart",
    "position": "20,1",
    "type_hint": null,
    "index": null
  }
]
''', d.to_json() )

  def test_find_backwards_by_name(self):
    d = btl_lexer_token_list()
    d.append( ( 'fruit', 'kiwi', ( 1, 1 ), None, None ) )
    d.append( ( 'color', 'red', ( 10, 1 ), 'h_color', None ) )
    d.append( ( 'flavor', 'tart', ( 20, 1 ), None, None ) )
    d.append( ( 'price', 'cheap', ( 30, 1 ), None, None ) )
    d.append( ( 'aisle', '42', ( 40, 1 ), None, None ) )

    self.assertEqual( ( 'price', 'cheap', ( 30, 1 ), None, None ),
                      d.find_backwards_by_name(4, 'price') )
    self.assertEqual( ( 'fruit', 'kiwi', ( 1, 1 ), None, None ),
                      d.find_backwards_by_name(3, 'fruit') )

  def test_find_backwards_by_line(self):
    t1 = btl_lexer_token('fruit', 'kiwi', ( 1, 1 ), None, None)
    t2 = btl_lexer_token('color', 'red', ( 1, 2 ), 'h_color', None)
    t3 = btl_lexer_token('flavor', 'tart', ( 2, 1 ), None, None)
    t4 = btl_lexer_token('price', 'cheap', ( 2, 2 ), None, None)
    t5 = btl_lexer_token('aisle', '42', ( 3, 1 ), None, None)
    d = btl_lexer_token_list([
      t1,
      t2,
      t3,
      t4,
      t5,
    ])
    self.assertEqual( t5, d.find_backwards_by_line(4, 3) )
    self.assertEqual( t2, d.find_backwards_by_line(4, 1) )
    self.assertEqual( t4, d.find_backwards_by_line(4, 2) )
    self.assertEqual( None, d.find_backwards_by_line(4, 42) )
    self.assertEqual( t1, d.find_backwards_by_line(0, 1) )

  def test_find_forwards_by_line(self):
    t1 = btl_lexer_token('fruit', 'kiwi', ( 1, 1 ), None, None)
    t2 = btl_lexer_token('color', 'red', ( 1, 2 ), 'h_color', None)
    t3 = btl_lexer_token('flavor', 'tart', ( 2, 1 ), None, None)
    t4 = btl_lexer_token('price', 'cheap', ( 2, 2 ), None, None)
    t5 = btl_lexer_token('aisle', '42', ( 3, 1 ), None, None)
    d = btl_lexer_token_list([
      t1,
      t2,
      t3,
      t4,
      t5,
    ])
    self.assertEqual( t5, d.find_forwards_by_line(0, 3) )
    self.assertEqual( t3, d.find_forwards_by_line(0, 2) )
    self.assertEqual( t1, d.find_forwards_by_line(0, 1) )
    self.assertEqual( None, d.find_forwards_by_line(0, 42) )
    self.assertEqual( t5, d.find_forwards_by_line(4, 3) )
    self.assertEqual( None, d.find_forwards_by_line(4, 42) )
    
  def test_first_line_to_index(self):
    l = btl_lexer_token_list([
      ( 'fruit', 'dragonfruit', ( 1, 1 ), None, 0 ),
      ( 'color', 'orange', ( 1, 3 ), 'h_color', 1 ),
      ( 'flavor', 'weird', ( 2, 1 ), None, 2 ),
      ( 'price', 'expensive', ( 2, 4 ), None, 3 ),
      ( 'foo', '1', ( 3, 1 ), None, 4 ),
      ( 'bar', '2', ( 5, 1 ), None, 5 ),
      ( 'baz', '3', ( 5, 6 ), None, 6 ),
    ])
    self.assertEqual( 0, l.first_line_to_index(1) )
    self.assertEqual( 2, l.first_line_to_index(2) )
    self.assertEqual( 4, l.first_line_to_index(3) )
    self.assertEqual( -1, l.first_line_to_index(4) )
    self.assertEqual( 5, l.first_line_to_index(5) )

  def test_last_line_to_index(self):
    l = btl_lexer_token_list([
      ( 'fruit', 'dragonfruit', ( 1, 1 ), None, 0 ),
      ( 'color', 'orange', ( 1, 3 ), 'h_color', 1 ),
      ( 'flavor', 'weird', ( 2, 1 ), None, 2 ),
      ( 'price', 'expensive', ( 2, 4 ), None, 3 ),
      ( 'foo', '1', ( 3, 1 ), None, 4 ),
      ( 'bar', '2', ( 5, 1 ), None, 5 ),
      ( 'baz', '3', ( 5, 6 ), None, 6 ),
    ])
    self.assertEqual( 1, l.last_line_to_index(1) )
    self.assertEqual( 3, l.last_line_to_index(2) )
    self.assertEqual( 4, l.last_line_to_index(3) )
    self.assertEqual( -1, l.last_line_to_index(4) )
    self.assertEqual( 6, l.last_line_to_index(5) )
    
  def test___getitem__slice(self):
    d = btl_lexer_token_list()
    d.append( ( 'fruit', 'kiwi', ( 1, 1 ), None, None ) )
    d.append( ( 'color', 'red', ( 10, 1 ), 'h_color', None ) )
    d.append( ( 'flavor', 'tart', ( 20, 1 ), None, None ) )
    d.append( ( 'price', 'cheap', ( 30, 1 ), None, None ) )
    d.append( ( 'aisle', '42', ( 40, 1 ), None, None ) )

    self.assertEqual( [
      ( 'fruit', 'kiwi', ( 1, 1 ), None, None ),
      ( 'color', 'red', ( 10, 1 ), 'h_color', None ),
    ], d[0:2] )

  def test___setitem__slice(self):
    d = btl_lexer_token_list()
    d.append( ( 'fruit', 'kiwi', ( 1, 1 ), None, None ) )
    d.append( ( 'color', 'red', ( 10, 1 ), 'h_color', None ) )
    d.append( ( 'flavor', 'tart', ( 20, 1 ), None, None ) )
    d.append( ( 'price', 'cheap', ( 30, 1 ), None, None ) )
    d.append( ( 'aisle', '42', ( 40, 1 ), None, None ) )
    d[0:2] = [
      ( 'cheese', 'brie', ( 2, 2 ), None, None ),
      ( 'flavor', 'yum', ( 20, 2 ), 'h_cheese', None ),
    ]
    self.assertEqual( [
      ( 'cheese', 'brie', ( 2, 2 ), None, None ),
      ( 'flavor', 'yum', ( 20, 2 ), 'h_cheese', None ),
      ( 'flavor', 'tart', ( 20, 1 ), None, None ),
      ( 'price', 'cheap', ( 30, 1 ), None, None ),
      ( 'aisle', '42', ( 40, 1 ), None, None ),
    ], d )

  def test_insert_values_middle(self):
    l1 = btl_lexer_token_list([
      ( 'fruit', 'dragonfruit', ( 4, 4 ), None, None ),
      ( 'color', 'orange', ( 23, 4 ), 'h_color', None ),
      ( 'flavor', 'weird', ( 2, 4 ), None, None ),
      ( 'price', 'expensive', ( 2, 4 ), None, None ),
    ])

    l2 = btl_lexer_token_list([
      ( 'foo', '1', ( 1, 1 ), None, None ),
      ( 'bar', '2', ( 1, 1 ), None, None ),
      ( 'baz', '3', ( 1, 1 ), None, None ),
    ])
    l1.insert_values(2, l2)
    self.assertEqual( [
      ( 'fruit', 'dragonfruit', ( 4, 4 ), None, None ),
      ( 'color', 'orange', ( 23, 4 ), 'h_color', None ),
      ( 'foo', '1', ( 1, 1 ), None, None ),
      ( 'bar', '2', ( 1, 1 ), None, None ),
      ( 'baz', '3', ( 1, 1 ), None, None ),
      ( 'flavor', 'weird', ( 2, 4 ), None, None ),
      ( 'price', 'expensive', ( 2, 4 ), None, None ),
    ], l1 )

  def test_insert_values_top(self):
    l1 = btl_lexer_token_list([
      ( 'fruit', 'dragonfruit', ( 4, 4 ), None, None ),
      ( 'color', 'orange', ( 23, 4 ), 'h_color', None ),
      ( 'flavor', 'weird', ( 2, 4 ), None, None ),
      ( 'price', 'expensive', ( 2, 4 ), None, None ),
    ])

    l2 = btl_lexer_token_list([
      ( 'foo', '1', ( 1, 1 ), None, None ),
      ( 'bar', '2', ( 1, 1 ), None, None ),
      ( 'baz', '3', ( 1, 1 ), None, None ),
    ])
    l1.insert_values(0, l2)
    self.assertEqual( [
      ( 'foo', '1', ( 1, 1 ), None, None ),
      ( 'bar', '2', ( 1, 1 ), None, None ),
      ( 'baz', '3', ( 1, 1 ), None, None ),
      ( 'fruit', 'dragonfruit', ( 4, 4 ), None, None ),
      ( 'color', 'orange', ( 23, 4 ), 'h_color', None ),
      ( 'flavor', 'weird', ( 2, 4 ), None, None ),
      ( 'price', 'expensive', ( 2, 4 ), None, None ),
    ], l1 )

  def test_insert_values_bottom(self):
    l1 = btl_lexer_token_list([
      ( 'fruit', 'dragonfruit', ( 4, 4 ), None, None ),
      ( 'color', 'orange', ( 23, 4 ), 'h_color', None ),
      ( 'flavor', 'weird', ( 2, 4 ), None, None ),
      ( 'price', 'expensive', ( 2, 4 ), None, None ),
    ])

    l2 = btl_lexer_token_list([
      ( 'foo', '1', ( 1, 1 ), None, None ),
      ( 'bar', '2', ( 1, 1 ), None, None ),
      ( 'baz', '3', ( 1, 1 ), None, None ),
    ])
    l1.insert_values(-1, l2)
    self.assertEqual( [
      ( 'fruit', 'dragonfruit', ( 4, 4 ), None, None ),
      ( 'color', 'orange', ( 23, 4 ), 'h_color', None ),
      ( 'flavor', 'weird', ( 2, 4 ), None, None ),
      ( 'price', 'expensive', ( 2, 4 ), None, None ),
      ( 'foo', '1', ( 1, 1 ), None, None ),
      ( 'bar', '2', ( 1, 1 ), None, None ),
      ( 'baz', '3', ( 1, 1 ), None, None ),
    ], l1 )

  def xtest_first_line_to_index(self):
    l = btl_lexer_token_list([
      ( 'fruit', 'dragonfruit', ( 1, 1 ), None, 0 ),
      ( 'color', 'orange', ( 1, 3 ), 'h_color', 1 ),
      ( 'flavor', 'weird', ( 2, 1 ), None, 2 ),
      ( 'price', 'expensive', ( 2, 4 ), None, 3 ),
      ( 'foo', '1', ( 3, 1 ), None, 4 ),
      ( 'bar', '2', ( 5, 1 ), None, 5 ),
      ( 'baz', '3', ( 5, 6 ), None, 6 ),
    ])
    self.assertEqual( 0, l.first_line_to_index(1) )
    return
    self.assertEqual( 2, l.first_line_to_index(2) )
    self.assertEqual( 4, l.first_line_to_index(3) )
    self.assertEqual( None, l.first_line_to_index(4) )
    self.assertEqual( 5, l.first_line_to_index(5) )
    
  def test_reorder_index_only(self):
    l = btl_lexer_token_list([
      ( 'fruit', 'dragonfruit', ( 1, 1 ), None, 0 ),
      ( 'fruit', 'orange', ( 1, 1 ), None, 0 ),
      ( 'color', 'orange', ( 1, 3 ), 'h_color', 1 ),
      ( 'flavor', 'weird', ( 2, 1 ), None, 2 ),
      ( 'price', 'expensive', ( 2, 4 ), None, 3 ),
      ( 'foo', '1', ( 3, 1 ), None, 4 ),
      ( 'bar', '2', ( 5, 1 ), None, 5 ),
      ( 'baz', '3', ( 5, 6 ), None, 6 ),
    ])
    l.reorder(0, 9)
    self.assert_multi_line_xp_equal('''\
0: fruit:dragonfruit:p=1,1:i=9
1: fruit:orange:p=1,1:i=10
2: color:orange:p=1,3:h=h_color:i=11
3: flavor:weird:p=2,1:i=12
4: price:expensive:p=2,4:i=13
5: foo:1:p=3,1:i=14
6: bar:2:p=5,1:i=15
7: baz:3:p=5,6:i=16
''', l.to_debug_str() )

  def test_reorder_line_only(self):
    l = btl_lexer_token_list([
      ( 'fruit', 'dragonfruit', ( 1, 1 ), None, 0 ),
      ( 'fruit', 'orange', ( 1, 1 ), None, 0 ),
      ( 'color', 'orange', ( 1, 3 ), 'h_color', 1 ),
      ( 'flavor', 'weird', ( 2, 1 ), None, 2 ),
      ( 'price', 'expensive', ( 2, 4 ), None, 3 ),
      ( 'foo', '1', ( 3, 1 ), None, 4 ),
      ( 'bar', '2', ( 5, 1 ), None, 5 ),
      ( 'baz', '3', ( 5, 6 ), None, 6 ),
    ])
    l.reorder(9, 0)
    self.assert_multi_line_xp_equal('''\
0: fruit:dragonfruit:p=10,1:i=0
1: fruit:orange:p=10,1:i=1
2: color:orange:p=10,3:h=h_color:i=2
3: flavor:weird:p=11,1:i=3
4: price:expensive:p=11,4:i=4
5: foo:1:p=12,1:i=5
6: bar:2:p=14,1:i=6
7: baz:3:p=14,6:i=7
''', l.to_debug_str() )

  def test_skip_index_right_by_name_one(self):
    l = btl_lexer_token_list([
      ( 'fruit', 'dragonfruit', ( 1, 1 ), None, 0 ),
      ( 'fruit', 'kiwi', ( 1, 3 ), 'h_color', 1 ),
      ( 'fruit', 'blueberry', ( 2, 1 ), None, 2 ),
      ( 'price', 'expensive', ( 2, 4 ), None, 3 ),
      ( 'foo', '1', ( 3, 1 ), None, 4 ),
      ( 'bar', '2', ( 5, 1 ), None, 5 ),
      ( 'baz', '3', ( 5, 6 ), None, 6 ),
    ])
    self.assertEqual( 1, l.skip_index_by_name(0, 'right', 'fruit', '1') )
    self.assertEqual( 2, l.skip_index_by_name(1, 'right', 'fruit', '1') )
    self.assertEqual( 4, l.skip_index_by_name(3, 'right', 'price', '1') )
    self.assertEqual( 3, l.skip_index_by_name(3, 'right', 'bar', '1') )
    self.assertEqual( 7, l.skip_index_by_name(6, 'right', 'baz', '1') )

  def test_skip_index_right_by_name_zero_or_one(self):
    l = btl_lexer_token_list([
      ( 'fruit', 'dragonfruit', ( 1, 1 ), None, 0 ),
      ( 'fruit', 'kiwi', ( 1, 3 ), 'h_color', 1 ),
      ( 'fruit', 'blueberry', ( 2, 1 ), None, 2 ),
      ( 'price', 'expensive', ( 2, 4 ), None, 3 ),
      ( 'foo', '1', ( 3, 1 ), None, 4 ),
      ( 'bar', '2', ( 5, 1 ), None, 5 ),
      ( 'baz', '3', ( 5, 6 ), None, 6 ),
    ])
    self.assertEqual( 1, l.skip_index_by_name(0, 'right', 'fruit', '?') )
    self.assertEqual( 2, l.skip_index_by_name(1, 'right', 'fruit', '?') )
    self.assertEqual( 4, l.skip_index_by_name(3, 'right', 'price', '?') )
    self.assertEqual( 3, l.skip_index_by_name(3, 'right', 'bar', '?') )
    self.assertEqual( 7, l.skip_index_by_name(6, 'right', 'baz', '?') )
    
  def test_skip_index_right_by_name_zero_or_more(self):
    l = btl_lexer_token_list([
      ( 'fruit', 'dragonfruit', ( 1, 1 ), None, 0 ),
      ( 'fruit', 'kiwi', ( 1, 3 ), 'h_color', 1 ),
      ( 'fruit', 'blueberry', ( 2, 1 ), None, 2 ),
      ( 'price', 'expensive', ( 2, 4 ), None, 3 ),
      ( 'foo', '1', ( 3, 1 ), None, 4 ),
      ( 'bar', '2', ( 5, 1 ), None, 5 ),
      ( 'baz', '3', ( 5, 6 ), None, 6 ),
    ])
    self.assertEqual( 3, l.skip_index_by_name(0, 'right', 'fruit', '*') )
    self.assertEqual( 3, l.skip_index_by_name(1, 'right', 'fruit', '*') )
    self.assertEqual( 4, l.skip_index_by_name(3, 'right', 'price', '*') )
    self.assertEqual( 3, l.skip_index_by_name(3, 'right', 'bar', '*') )
    self.assertEqual( 7, l.skip_index_by_name(6, 'right', 'baz', '*') )

  def test_skip_index_right_by_name_all_but_one(self):
    l = btl_lexer_token_list([
      ( 'fruit', 'dragonfruit', ( 1, 1 ), None, 0 ),
      ( 'fruit', 'kiwi', ( 1, 3 ), 'h_color', 1 ),
      ( 'fruit', 'blueberry', ( 2, 1 ), None, 2 ),
      ( 'price', 'expensive', ( 2, 4 ), None, 3 ),
      ( 'foo', '1', ( 3, 1 ), None, 4 ),
      ( 'bar', '2', ( 5, 1 ), None, 5 ),
      ( 'baz', '3', ( 5, 6 ), None, 6 ),
    ])
    self.assertEqual( 2, l.skip_index_by_name(0, 'right', 'fruit', '^') )
    self.assertEqual( 2, l.skip_index_by_name(1, 'right', 'fruit', '^') )
    self.assertEqual( 3, l.skip_index_by_name(3, 'right', 'price', '^') )
    self.assertEqual( 3, l.skip_index_by_name(3, 'right', 'bar', '^') )
    self.assertEqual( 6, l.skip_index_by_name(6, 'right', 'baz', '^') )
    
  def test_skip_index_right_by_name_one_or_more(self):
    l = btl_lexer_token_list([
      ( 'fruit', 'dragonfruit', ( 1, 1 ), None, 0 ),
      ( 'fruit', 'kiwi', ( 1, 3 ), 'h_color', 1 ),
      ( 'fruit', 'blueberry', ( 2, 1 ), None, 2 ),
      ( 'price', 'expensive', ( 2, 4 ), None, 3 ),
      ( 'foo', '1', ( 3, 1 ), None, 4 ),
      ( 'bar', '2', ( 5, 1 ), None, 5 ),
      ( 'baz', '3', ( 5, 6 ), None, 6 ),
    ])
    self.assertEqual( 3, l.skip_index_by_name(0, 'right', 'fruit', '+') )
    self.assertEqual( 3, l.skip_index_by_name(1, 'right', 'fruit', '+') )
    self.assertEqual( 4, l.skip_index_by_name(3, 'right', 'price', '+') )
    self.assertEqual( 3, l.skip_index_by_name(3, 'right', 'bar', '+') )
    self.assertEqual( 7, l.skip_index_by_name(6, 'right', 'baz', '+') )

  def xtest_skip_index_left_by_name_one(self):
    l = btl_lexer_token_list([
      ( 'fruit', 'dragonfruit', ( 1, 1 ), None, 0 ),
      ( 'fruit', 'kiwi', ( 1, 3 ), 'h_color', 1 ),
      ( 'fruit', 'blueberry', ( 2, 1 ), None, 2 ),
      ( 'price', 'expensive', ( 2, 4 ), None, 3 ),
      ( 'foo', '1', ( 3, 1 ), None, 4 ),
      ( 'bar', '2', ( 5, 1 ), None, 5 ),
      ( 'baz', '3', ( 5, 6 ), None, 6 ),
    ])
    self.assertEqual( -1, l.skip_index_by_name(0, 'left', 'fruit', '1') )
    self.assertEqual( 0, l.skip_index_by_name(1, 'left', 'fruit', '1') )
    self.assertEqual( 1, l.skip_index_by_name(2, 'left', 'fruit', '1') )
    self.assertEqual( 2, l.skip_index_by_name(3, 'left', 'price', '1') )
    self.assertEqual( None, l.skip_index_by_name(3, 'left', 'bar', '1') )
    self.assertEqual( 7, l.skip_index_by_name(6, 'left', 'baz', '1') )

  def xtest_skip_index_left_by_name_zero_or_one(self):
    l = btl_lexer_token_list([
      ( 'fruit', 'dragonfruit', ( 1, 1 ), None, 0 ),
      ( 'fruit', 'kiwi', ( 1, 3 ), 'h_color', 1 ),
      ( 'fruit', 'blueberry', ( 2, 1 ), None, 2 ),
      ( 'price', 'expensive', ( 2, 4 ), None, 3 ),
      ( 'foo', '1', ( 3, 1 ), None, 4 ),
      ( 'bar', '2', ( 5, 1 ), None, 5 ),
      ( 'baz', '3', ( 5, 6 ), None, 6 ),
    ])
    self.assertEqual( 1, l.skip_index_by_name(0, 'left', 'fruit', '?') )
    self.assertEqual( 2, l.skip_index_by_name(1, 'left', 'fruit', '?') )
    self.assertEqual( 4, l.skip_index_by_name(3, 'left', 'price', '?') )
    self.assertEqual( 3, l.skip_index_by_name(3, 'left', 'bar', '?') )
    self.assertEqual( 7, l.skip_index_by_name(6, 'left', 'baz', '?') )
    
  def xtest_skip_index_left_by_name_zero_or_more(self):
    l = btl_lexer_token_list([
      ( 'fruit', 'dragonfruit', ( 1, 1 ), None, 0 ),
      ( 'fruit', 'kiwi', ( 1, 3 ), 'h_color', 1 ),
      ( 'fruit', 'blueberry', ( 2, 1 ), None, 2 ),
      ( 'price', 'expensive', ( 2, 4 ), None, 3 ),
      ( 'foo', '1', ( 3, 1 ), None, 4 ),
      ( 'bar', '2', ( 5, 1 ), None, 5 ),
      ( 'baz', '3', ( 5, 6 ), None, 6 ),
    ])
    self.assertEqual( 3, l.skip_index_by_name(0, 'left', 'fruit', '*') )
    self.assertEqual( 3, l.skip_index_by_name(1, 'left', 'fruit', '*') )
    self.assertEqual( 4, l.skip_index_by_name(3, 'left', 'price', '*') )
    self.assertEqual( 3, l.skip_index_by_name(3, 'left', 'bar', '*') )
    self.assertEqual( 7, l.skip_index_by_name(6, 'left', 'baz', '*') )

  def xtest_skip_index_left_by_name_one_or_more(self):
    l = btl_lexer_token_list([
      ( 'fruit', 'dragonfruit', ( 1, 1 ), None, 0 ),
      ( 'fruit', 'kiwi', ( 1, 3 ), 'h_color', 1 ),
      ( 'fruit', 'blueberry', ( 2, 1 ), None, 2 ),
      ( 'price', 'expensive', ( 2, 4 ), None, 3 ),
      ( 'foo', '1', ( 3, 1 ), None, 4 ),
      ( 'bar', '2', ( 5, 1 ), None, 5 ),
      ( 'baz', '3', ( 5, 6 ), None, 6 ),
    ])
    self.assertEqual( 3, l.skip_index_by_name(0, 'left', 'fruit', '+') )
    self.assertEqual( 3, l.skip_index_by_name(1, 'left', 'fruit', '+') )
    self.assertEqual( 4, l.skip_index_by_name(3, 'left', 'price', '+') )
    self.assertEqual( 3, l.skip_index_by_name(3, 'left', 'bar', '+') )
    self.assertEqual( 7, l.skip_index_by_name(6, 'left', 'baz', '+') )

  def test_skip_index_by_name_zero_or_more_boundary(self):
    l = btl_lexer_token_list([
      ( 't_line_break', '\n', ( 1, 1 ), 'h_line_break', 0 ),
      ( 't_line_break', '\n', ( 2, 1 ), 'h_line_break', 1 ),
    ])
    self.assertEqual( 2, l.skip_index_by_name(1, 'right', 't_line_break', '*') )
    self.assertEqual( 0, l.skip_index_by_name(0, 'left', 't_line_break', '*') )

  def test_has_left_line_break(self):
    l = btl_lexer_token_list([
      ( 't_line_break', '\n', ( 1, 1 ), 'h_line_break', 0 ),
      ( 't_line_break', '\n', ( 2, 1 ), 'h_line_break', 1 ),
    ])
    self.assertEqual( None, l.has_left_line_break(0) )
    self.assertEqual( True, l.has_left_line_break(1) )
    self.assertEqual( True, l.has_left_line_break(2) )

  def test_has_right_line_break(self):
    l = btl_lexer_token_list([
      ( 't_line_break', '\n', ( 1, 1 ), 'h_line_break', 0 ),
      ( 't_line_break', '\n', ( 2, 1 ), 'h_line_break', 1 ),
    ])
    self.assertEqual( True, l.has_right_line_break(-1) )
    self.assertEqual( True, l.has_right_line_break(0) )
    self.assertEqual( None, l.has_right_line_break(1) )
    
if __name__ == '__main__':
  unit_test.main()

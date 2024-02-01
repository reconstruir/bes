#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.btl.btl_parser_desc_char import btl_parser_desc_char
from bes.btl.btl_parser_desc_char_map import btl_parser_desc_char_map
from bes.btl.btl_error import btl_error
from bes.testing.unit_test import unit_test

class test_test_btl_parser_desc_char_map(unit_test):

  _NUMERIC = set([ c for c in '0123456789' ])
  _ALPHA_LOWER = set([ c for c in 'abcdefghijklmnopqrstuvwxyz' ])
  _ALPHA_UPPER = set([ c for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' ])
  _ALPHA = _ALPHA_LOWER | _ALPHA_UPPER
  _ALPHA_NUMERIC = _ALPHA | _NUMERIC
  
  def test___getitem__(self):
    m = btl_parser_desc_char_map()
    self.assertEqual( ( 'c_amp', { '&' } ), m['c_amp'] )
    self.assertEqual( ( 'c_numeric', self._NUMERIC ), m['c_numeric'] )

  def test_parse_union(self):
    m = btl_parser_desc_char_map()
    self.assertEqual( self._NUMERIC, m.parse_union('c_numeric') )
    self.assertEqual( self._NUMERIC | { '_' }, m.parse_union('c_numeric|c_underscore') )
    self.assertEqual( self._NUMERIC | { '_' }, m.parse_union('c_numeric|_') )
    self.assertEqual( { '&' }, m.parse_union('&') )
    self.assertEqual( { '^' }, m.parse_union('^') )
    self.assertEqual( { '&', '^' }, m.parse_union('&|^') )
    self.assertEqual( { '&', '^' }, m.parse_union('^|&') )

  def test_parse_union_unknown_char(self):
    m = btl_parser_desc_char_map()
    with self.assertRaises(btl_error) as _:
      m.parse_union('c_not_there')

  def test_add(self):
    m = btl_parser_desc_char_map()
    m.add(btl_parser_desc_char('kiwi', { 'A', 'B' }))
    m.add(btl_parser_desc_char('lemon', { 'C', 'D' }))
    #print(m.to_json())
    self.assert_json_equal('''
{
  "kiwi": {
    "name": "kiwi", 
    "chars": [
      "A", 
      "B" 
    ]
  }, 
  "lemon": {
    "name": "lemon", 
    "chars": [
      "C", 
      "D" 
    ]
  }
}
''', m.to_json() )

  def test_from_json(self):
    expected = '''
{
  "kiwi": {
    "name": "kiwi", 
    "chars": [
      "A", 
      "B"
    ]
  }, 
  "lemon": {
    "name": "lemon", 
    "chars": [
      "C", 
      "D"
    ]
  }
}
'''
    self.assert_json_equal( expected, btl_parser_desc_char_map.from_json(expected).to_json() )
    
if __name__ == '__main__':
  unit_test.main()

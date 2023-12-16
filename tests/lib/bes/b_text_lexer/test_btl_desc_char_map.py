#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.b_text_lexer.btl_desc_char import btl_desc_char
from bes.b_text_lexer.btl_desc_char_map import btl_desc_char_map
from bes.b_text_lexer.btl_error import btl_error
from bes.testing.unit_test import unit_test

class test_test_btl_desc_char_map(unit_test):

  _NUMERIC = set([ ord(c) for c in '0123456789' ])
  _ALPHA_LOWER = set([ ord(c) for c in 'abcdefghijklmnopqrstuvwxyz' ])
  _ALPHA_UPPER = set([ ord(c) for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' ])
  _ALPHA = _ALPHA_LOWER | _ALPHA_UPPER
  _ALPHA_NUMERIC = _ALPHA | _NUMERIC
  
  def test___getitem__(self):
    m = btl_desc_char_map()
    self.assertEqual( ( 'c_amp', { ord('&') } ), m['c_amp'] )
    self.assertEqual( ( 'c_numeric', self._NUMERIC ), m['c_numeric'] )

  def test_parse_union(self):
    m = btl_desc_char_map()
    self.assertEqual( self._NUMERIC, m.parse_union('c_numeric') )
    self.assertEqual( self._NUMERIC | { ord('_') }, m.parse_union('c_numeric|c_underscore') )
    self.assertEqual( self._NUMERIC | { ord('_') }, m.parse_union('c_numeric|_') )

  def test_parse_union_unknown_char(self):
    m = btl_desc_char_map()
    with self.assertRaises(btl_error) as _:
      m.parse_union('c_not_there')
    
if __name__ == '__main__':
  unit_test.main()

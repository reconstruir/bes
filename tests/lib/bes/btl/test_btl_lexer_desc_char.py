#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.btl.btl_lexer_desc_char import btl_lexer_desc_char
from bes.testing.unit_test import unit_test

class test_test_btl_lexer_desc_char(unit_test):

  def test_as_dict_from(self):
    self.assertEqual( {
      'name': 'kiwi',
      'chars': [ 'A' ],
      }, btl_lexer_desc_char('kiwi', { 'A' }).as_dict )
    self.assertEqual( {
      'name': 'kiwi',
      'chars': [ 'A', 'B' ],
      }, btl_lexer_desc_char('kiwi', { 'A', 'B' }).as_dict )
    
if __name__ == '__main__':
  unit_test.main()

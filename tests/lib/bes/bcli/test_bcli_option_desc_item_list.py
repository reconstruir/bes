#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import typing
#import datetime
from datetime import datetime
#from datetime import timedelta

from bes.testing.unit_test import unit_test
from bes.bcli.bcli_option_desc_item import bcli_option_desc_item
from bes.bcli.bcli_option_desc_item_list import bcli_option_desc_item_list
from bes.bcli.bcli_type_manager import bcli_type_manager

class test_bcli_option_desc_item_list(unit_test):

  def test_parse_text(self):
    m = bcli_type_manager()
    text = '''
kiwi list[int] default=[]
lemon list[str] default=[]
melon list[str] default=[]
'''
    self.assertEqual( [
      ( 'kiwi', 'list', typing.List[int], [], False ),
      ( 'lemon', 'list', typing.List[str], [], False ),
      ( 'melon', 'list', typing.List[str], [], False ),
    ], bcli_option_desc_item_list.parse_text(m, text) )

  def test_to_dict(self):
    m = bcli_type_manager()
    text = '''
kiwi list[int] default=[]
lemon list[str] default=[]
melon list[str] default=[]
'''
    self.assertEqual( {
      'kiwi': ( 'kiwi', 'list', typing.List[int], [], False ),
      'lemon': ( 'lemon', 'list', typing.List[str], [], False ),
      'melon': ( 'melon', 'list', typing.List[str], [], False ),
    }, bcli_option_desc_item_list.parse_text(m, text).to_dict() )

  def test_to_dict_with_duplicate_name(self):
    m = bcli_type_manager()
    text = '''
kiwi list[int] default=[]
kiwi list[str] default=[]
'''
    with self.assertRaises(KeyError) as ctx:
      bcli_option_desc_item_list.parse_text(m, text).to_dict()

  def test_parse_text_with_defaults(self):
    m = bcli_type_manager()
    m.add_variable('_default_melon', lambda: [ 'a', 'b', 'c' ])
    text = '''
kiwi int default=42
pear int default=None
lemon list[str] default=[]
melon list[str] default=${_default_melon}
'''
    self.assertEqual( [
      ( 'kiwi', 'int', int, 42, False ),
      ( 'pear', 'int', int, None, False ),
      ( 'lemon', 'list', typing.List[str], [], False ),
      ( 'melon', 'list', typing.List[str], [ 'a', 'b', 'c' ], False ),
    ], bcli_option_desc_item_list.parse_text(m, text) )
    
  def test_parse_text_with_variables(self):
    m = bcli_type_manager()
    m.add_variable('bcli_foo', lambda: '42')
    m.add_variable('bcli_bar', lambda: '666')
    text = '''
kiwi int default=${bcli_foo}
pear int default=${bcli_bar}
'''
    self.assertEqual( [
      ( 'kiwi', 'int', int, 42, False ),
      ( 'pear', 'int', int, 666, False ),
    ], bcli_option_desc_item_list.parse_text(m, text) )

  def test_parse_text_with_non_constant_variables(self):
    m = bcli_type_manager()
    l = [ 0 ]
    def _value():
      l[0] += 1
      return l[0]
    m.add_variable('bcli_foo', _value)
    m.add_variable('bcli_bar', _value)
    text = '''
kiwi int default=${bcli_foo}
pear int default=${bcli_bar}
'''
    self.assertEqual( [
      ( 'kiwi', 'int', int, 1, False ),
      ( 'pear', 'int', int, 2, False ),
    ], bcli_option_desc_item_list.parse_text(m, text) )

if __name__ == '__main__':
  unit_test.main()

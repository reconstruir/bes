#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import typing
#from datetime import datetime
#from datetime import timedelta

from bes.testing.unit_test import unit_test
from bes.bcli.bcli_option_desc_item import bcli_option_desc_item
from bes.bcli.bcli_type_manager import bcli_type_manager

class test_bcli_option_desc_item(unit_test):
  
  def test___init__simple(self):
    item = bcli_option_desc_item('kiwi', 'int', int, None, False)

  def test___init__typing(self):
    item = bcli_option_desc_item('kiwi', 'list', typing.List[int], [], False)

  def test_parse_text_basic(self):
    self.maxDiff = None
    m = bcli_type_manager()
    self.assert_json_equal('''
{
  "name": "kiwi",
  "type_name": "list",
  "option_type": "typing.List[int]",
  "default": [],
  "secret": false
}    
''', bcli_option_desc_item.parse_text(m, 'kiwi list[int] default=[]').to_json() )

  def test_parse_text_with_defaults(self):
    m = bcli_type_manager()
    m.add_variable('_default', lambda: [ 'a', 'b', 'c' ])
    self.assertEqual( ( 'kiwi', 'list', typing.List[str], [ 'a', 'b', 'c' ], False ),
                      bcli_option_desc_item.parse_text(m, 'kiwi list[str] default=${_default}') )

  def test_to_dict(self):
    m = bcli_type_manager()
    self.assertEqual( {
      'name': 'kiwi',
      'type_name': 'list',
      'option_type': typing.List[int],
      'default': [],
      'secret': False,
    }, bcli_option_desc_item('kiwi', 'list', typing.List[int], [], False).to_dict() )

  def test_to_json(self):
    m = bcli_type_manager()
    self.assert_json_equal( '''
{
  "name": "kiwi",
  "type_name": "list",
  "option_type": "typing.List[int]",
  "default": [],
  "secret": false
}
''', bcli_option_desc_item('kiwi', 'list', typing.List[int], [], False).to_json() )
    
  def test__parse_parts(self):
    self.assertEqual( ( 'kiwi', 'list[int]', { 'default': '[]' } ),
                      bcli_option_desc_item._parse_parts('kiwi list[int] default=[]') )
    
  def test__parse_parts_default_string_with_spaces(self):
    self.assertEqual( ( 'kiwi', 'str', { 'default': '"string with spaces"' } ),
                      bcli_option_desc_item._parse_parts('kiwi str default="string with spaces"') )
    
  def test__parse_parts_multiple_key_values(self):
    self.assertEqual( ( 'kiwi', 'list[int]', { 'default': '[]', 'secret': 'True' } ),
                      bcli_option_desc_item._parse_parts('kiwi list[int] default=[] secret=True') )

  def test__parse_parts_multiple_key_values(self):
    self.assertEqual( ( 'kiwi', 'list[int]', { 'default': '[]', 'secret': 'True' } ),
                      bcli_option_desc_item._parse_parts('kiwi list[int] default=[] secret=True') )
    
if __name__ == '__main__':
  unit_test.main()

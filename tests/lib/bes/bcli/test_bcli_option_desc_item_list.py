#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import typing
#import datetime
from datetime import datetime
#from datetime import timedelta

from bes.testing.unit_test import unit_test
from bes.bcli.bcli_option_desc_item import bcli_option_desc_item
from bes.bcli.bcli_option_desc_item_list import bcli_option_desc_item_list
from bes.bcli.bcli_simple_type_manager import bcli_simple_type_manager

class test_bcli_option_desc_item_list(unit_test):

  def test_parse_text(self):
    m = bcli_simple_type_manager()
    text = '''
kiwi list[int] []
lemon list[str] []
melon list[str] [ 'a', 'b', 'c' ]
'''
    self.assertEqual( [
      ( 'kiwi', typing.List[int], [] ),
      ( 'lemon', typing.List[str], [] ),
      ( 'melon', typing.List[str], [ 'a', 'b', 'c' ] ),
    ], bcli_option_desc_item_list.parse_text(m, text) )

  def test_to_dict(self):
    m = bcli_simple_type_manager()
    text = '''
kiwi list[int] []
lemon list[str] []
melon list[str] [ 'a', 'b', 'c' ]
'''
    self.assertEqual( {
      'kiwi': ( 'kiwi', typing.List[int], [] ),
      'lemon': ( 'lemon', typing.List[str], [] ),
      'melon': ( 'melon', typing.List[str], [ 'a', 'b', 'c' ] ),
    }, bcli_option_desc_item_list.parse_text(m, text).to_dict() )

  def test_to_dict_with_duplicate_name(self):
    m = bcli_simple_type_manager()
    text = '''
kiwi list[int] []
kiwi list[str] []
'''
    with self.assertRaises(KeyError) as ctx:
      bcli_option_desc_item_list.parse_text(m, text).to_dict()

  def test_parse_text_with_lambda_default(self):
    m = bcli_simple_type_manager()
    items = bcli_option_desc_item_list([ ( 'kiwi', datetime, lambda: datetime.now() ) ])
#    text = f'''
#kiwi datetime default:kiwi
#'''
#   items = bcli_option_desc_item_list.parse_text(text)
 #   from datetime import datetime
#    default_value = items[0].default_value()
#    self.assertEqual( 'kiwi', items[0].name )
#    self.assertEqual( datetime, items[0].option_type )
#    from datetime import datetime
#    self.assertEqual( 'datetime', type(items[0].default_value()).__name__ )
      
if __name__ == '__main__':
  unit_test.main()

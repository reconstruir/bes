#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import typing
#from datetime import datetime
#from datetime import timedelta

from bes.testing.unit_test import unit_test
from bes.bcli.bcli_option_desc_item import bcli_option_desc_item
from bes.bcli.bcli_option_desc_item_list import bcli_option_desc_item_list

class test_bcli_option_desc_item_list(unit_test):

  def test_parse_text(self):
    text = '''
kiwi list[int] []
lemon list[str] []
melon list[str] [ 'a', 'b', 'c' ]
'''
    self.assertEqual( [
      ( 'kiwi', typing.List[int], [] ),
      ( 'lemon', typing.List[str], [] ),
      ( 'melon', typing.List[str], [ 'a', 'b', 'c' ] ),
    ], bcli_option_desc_item_list.parse_text(text) )

  def test_to_dict(self):
    text = '''
kiwi list[int] []
lemon list[str] []
melon list[str] [ 'a', 'b', 'c' ]
'''
    self.assertEqual( {
      'kiwi': ( 'kiwi', typing.List[int], [] ),
      'lemon': ( 'lemon', typing.List[str], [] ),
      'melon': ( 'melon', typing.List[str], [ 'a', 'b', 'c' ] ),
    }, bcli_option_desc_item_list.parse_text(text).to_dict() )
    
if __name__ == '__main__':
  unit_test.main()

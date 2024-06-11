#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import typing
#from datetime import datetime
#from datetime import timedelta

from bes.testing.unit_test import unit_test
from bes.bcli.bcli_option_desc_item import bcli_option_desc_item
from bes.bcli.bcli_simple_type_manager import bcli_simple_type_manager

class test_bcli_option_desc_item(unit_test):

  def test___init__simple(self):
    item = bcli_option_desc_item('kiwi', int, None)

  def test___init__typing(self):
    item = bcli_option_desc_item('kiwi', typing.List[int], [])

  def test_parse_text(self):
    m = bcli_simple_type_manager()
#    p = bcli_option_desc_item.parse_text(m, 'kiwi list[int] []')
    self.assertEqual( ( 'kiwi', typing.List[int], [] ),
                      bcli_option_desc_item.parse_text(m, 'kiwi list[int] []') )
    
if __name__ == '__main__':
  unit_test.main()

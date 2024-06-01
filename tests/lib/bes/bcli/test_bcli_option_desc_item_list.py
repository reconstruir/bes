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
'''
    self.assertEqual( [
      ( 'kiwi', typing.List[int], [] ),
      ( 'lemon', typing.List[str], [] ),
    ], bcli_option_desc_item_list.parse_text(text) )

if __name__ == '__main__':
  unit_test.main()

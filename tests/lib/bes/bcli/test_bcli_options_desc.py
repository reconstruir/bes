#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import typing
from datetime import datetime
#from datetime import timedelta

from bes.testing.unit_test import unit_test
from bes.bcli.bcli_options_desc import bcli_options_desc
from bes.bcli.bcli_option_desc_item import bcli_option_desc_item
from bes.bcli.bcli_simple_type_item_list import bcli_simple_type_item_list

from _unit_test_kiwi_options_desc import _unit_test_kiwi_options_desc

class test_bcli_options_desc(unit_test):

  def test___init__(self):
    desc = _unit_test_kiwi_options_desc()
    self.assertEqual( '_kiwi_options_desc', desc.name() )
    self.assertEqual( [], desc.types() )
    self.assertEqual( True, desc.has_option('kiwi') )
    self.assertEqual( True, desc.has_option('pear') )
    self.assertEqual( False, desc.has_option('notthere') )
    self.assertEqual( 42, desc.default_value('kiwi') )
    self.assertEqual( 666, desc.default_value('pear') )

    self.assertEqual( True, desc.check_value_type('kiwi', 13) )
    self.assertEqual( False, desc.check_value_type('kiwi', '13') )

    self.assertEqual( {
      'kiwi': bcli_option_desc_item('kiwi', int, 42),
      'pear': bcli_option_desc_item('pear', int, 666),
    }, desc.items_dict )
    
if __name__ == '__main__':
  unit_test.main()

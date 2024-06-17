#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import typing
from datetime import datetime
#from datetime import timedelta

from bes.testing.unit_test import unit_test
from bes.bcli.bcli_options_desc import bcli_options_desc
from bes.bcli.bcli_simple_type_item_list import bcli_simple_type_item_list

from _unit_test_kiwi_options_desc import _unit_test_kiwi_options_desc

class test_bcli_options_desc(unit_test):

  def test___init__(self):
    desc = _unit_test_kiwi_options_desc()
    
if __name__ == '__main__':
  unit_test.main()

#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import typing
from datetime import datetime
from datetime import timedelta

from bes.testing.unit_test import unit_test
from bes.bcli.bcli_simple_type_item import bcli_simple_type_item
from bes.bcli.bcli_simple_type_manager import bcli_simple_type_manager

class test_bcli_simple_type_manager(unit_test):

  def test_basic_types(self):
    m = bcli_simple_type_manager()
    self.assertEqual( None, m.default('int') )

  def test__parse_type_str(self):
    f = bcli_simple_type_manager._parse_type_str
    self.assertEqual( ( 'list', 'int' ), f('list[int]') )
    self.assertEqual( ( 'int', None ), f('int') )
    
if __name__ == '__main__':
  unit_test.main()

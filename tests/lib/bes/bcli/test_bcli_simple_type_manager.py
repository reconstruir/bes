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
    self.assertEqual( int, m.type('int') )

  def test__parse_type_str(self):
    m = bcli_simple_type_manager()
    self.assertEqual( ( 'list', 'int' ), m._parse_type_str('list[int]') )
    self.assertEqual( ( 'int', None ), m._parse_type_str('int') )

  def test__parse_type_str_to_typing(self):
    m = bcli_simple_type_manager()
    self.assertEqual( typing.List[int], m._parse_type_str_to_typing('list[int]') )
    self.assertEqual( int, m._parse_type_str_to_typing('int') )
    
if __name__ == '__main__':
  unit_test.main()

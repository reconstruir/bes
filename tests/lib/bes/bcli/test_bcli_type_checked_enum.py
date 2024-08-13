#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.bcli.bcli_type_checked_enum import bcli_type_checked_enum
from bes.enum_util.checked_enum import checked_enum
from bes.system.check import check

class _fruit_bar_type(checked_enum):
  APPLE = 'apple'
  KIWI = 'kiwi'
  ORANGE = 'orange'
_fruit_bar_type.register_check_class()

class test_bcli_type_checked_enum(unit_test):

  class _fruit_bar_cli_type(bcli_type_checked_enum):
    __enum_class__ = _fruit_bar_type
  
  def test_parse(self):
    self.assertEqual( _fruit_bar_type.APPLE, self._fruit_bar_cli_type().parse('apple') )

  def test_check(self):
    self.assertEqual( _fruit_bar_type.ORANGE, self._fruit_bar_cli_type().check(_fruit_bar_type.ORANGE) )

  def test_type_function(self):
    self.assertEqual( _fruit_bar_type, self._fruit_bar_cli_type().type_function() )

  def test_type(self):
    self.assertEqual( _fruit_bar_type, self._fruit_bar_cli_type().type )

if __name__ == '__main__':
  unit_test.main()

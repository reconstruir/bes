#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.bcli.bcli_type_i import bcli_type_i
from bes.enum_util.checked_enum import checked_enum
from bes.system.check import check

class test_bcli_type_i(unit_test):

  class _fruit_foo_type(checked_enum):
    APPLE = 'apple'
    KIWI = 'kiwi'
    ORANGE = 'orange'
  _fruit_foo_type.register_check_class()

  class _fruit_foo_cli_type(bcli_type_i):

    @classmethod
    #@abstractmethod
    def name_str(clazz):
      return '_fruit_foo_type'

    @classmethod
    #@abstractmethod
    def type_function(clazz):
      return test_bcli_type_i._fruit_foo_type

    @classmethod
    #@abstractmethod
    def parse(clazz, text):
      return test_bcli_type_i._fruit_foo_type.parse_string(text)

    @classmethod
    #@abstractmethod
    def check(clazz, value, allow_none = False):
      return check.check__fruit_foo_type(value, allow_none = allow_none)
  
  def test_parse(self):
    self.assertEqual( self._fruit_foo_type.APPLE, self._fruit_foo_cli_type().parse('apple') )

  def test_check(self):
    self.assertEqual( self._fruit_foo_type.ORANGE, self._fruit_foo_cli_type().check(self._fruit_foo_type.ORANGE) )

  def test_type_function(self):
    self.assertEqual( self._fruit_foo_type, self._fruit_foo_cli_type().type_function() )

  def test_type(self):
    self.assertEqual( self._fruit_foo_type, self._fruit_foo_cli_type().type )

if __name__ == '__main__':
  unit_test.main()

#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import typing
from datetime import datetime
#from datetime import timedelta

from bes.testing.unit_test import unit_test

from bes.bcli.bcli_options import bcli_options
from bes.bcli.bcli_options_desc import bcli_options_desc
from bes.bcli.bcli_simple_type_item_list import bcli_simple_type_item_list

class test_bcli_options(unit_test):

  def test___getattr__(self):
    options = self._make_test_options()

  @classmethod
  def _make_test_options(clazz):
    types = bcli_simple_type_item_list([
    ])
    items_desc = '''
kiwi int ${bcli_foo}
pear int ${bcli_bar}
'''
    variables = {
      'bcli_foo': lambda: '42',
      'bcli_bar': lambda: '666',
    }
    desc = bcli_options_desc('foo', types, items_desc, variables)
    return bcli_options(desc)
    
if __name__ == '__main__':
  unit_test.main()

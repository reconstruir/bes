#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import typing
#from datetime import datetime
#from datetime import timedelta

from bes.testing.unit_test import unit_test
from bes.bcli.bcli_simple_type_item import bcli_simple_type_item

class test_bcli_simple_type_item(unit_test):

  def test_type(self):
    self.assertEqual( int, bcli_simple_type_item('kiwi', lambda: int, lambda: 666).type )

  def test_default(self):
    self.assertEqual( 666, bcli_simple_type_item('kiwi', lambda: int, lambda: 666).default )
    
if __name__ == '__main__':
  unit_test.main()

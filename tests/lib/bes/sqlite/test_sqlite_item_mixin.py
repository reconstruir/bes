#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.testing.unit_test import unit_test
from bes.sqlite.sqlite_item_mixin import sqlite_item_mixin

class test_sqlite_item_mixin(unit_test):

  class _fruit(namedtuple('_fruit', 'color, flavor, price'), sqlite_item_mixin):
    def __new__(clazz, color, flavor, price):
      return clazz.__bases__[0].__new__(clazz, color, flavor, price)

  def test_sql_for_insert(self):
    self.assertEqual( 'insert into fruits(color, flavor, price) values(?, ?, ?)',
                      self._fruit('red', 'apple', 1.42).sql_for_insert('fruits') )

  def test_sql_for_replace(self):
    self.assertEqual( 'replace into fruits(color, flavor, price) values(?, ?, ?)',
                      self._fruit('red', 'apple', 1.42).sql_for_replace('fruits') )
    
if __name__ == '__main__':
  unit_test.main()

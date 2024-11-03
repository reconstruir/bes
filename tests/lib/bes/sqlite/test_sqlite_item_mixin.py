#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.testing.unit_test import unit_test
from bes.sqlite.sqlite_item_mixin import sqlite_item_mixin

class test_sqlite_item_mixin(unit_test):

  class _fruit(namedtuple('_fruit', 'name, color, price'), sqlite_item_mixin):
    def __new__(clazz, name, color, price):
      return clazz.__bases__[0].__new__(clazz, name, color, price)

  def test_sql_for_insert(self):
    self.assertEqual( 'insert into fruits(name, color, price) values(?, ?, ?)',
                      self._fruit('apple', 'red', 1.42).sql_for_insert('fruits') )

  def test_sql_for_insert_with_exclude(self):
    self.assertEqual( 'insert into fruits(name, price) values(?, ?)',
                      self._fruit('apple', 'red', 1.42).sql_for_insert('fruits', exclude = set([ 'color' ])) )
    
  def test_sql_for_replace(self):
    self.assertEqual( 'replace into fruits(name, color, price) values(?, ?, ?)',
                      self._fruit('apple', 'red', 1.42).sql_for_replace('fruits') )

  def test_sql_for_replace_with_exclude(self):
    self.assertEqual( 'replace into fruits(name, price) values(?, ?)',
                      self._fruit('apple', 'red', 1.42).sql_for_replace('fruits', exclude = set([ 'color' ])) )
    
  def test_from_sql_row(self):
    self.assertEqual( ( 'apple', 'red', 1.42 ), self._fruit.from_sql_row(( 'apple', 'red', 1.42 )) )
    
if __name__ == '__main__':
  unit_test.main()

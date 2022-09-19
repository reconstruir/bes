#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test

from datetime import datetime

from bes.common.date_util import date_util

class test_date_util(unit_test):

  @classmethod
  def _date_to_string(clazz, s):
    return datetime.strptime(s, '%Y-%m-%d %H:%M:%S')

  @classmethod
  def _call_compare(clazz, d1, d2, operator):
    return date_util.compare(clazz._date_to_string(d1),
                             clazz._date_to_string(d2),
                             operator)
  
  def test_compare_eq(self):
    self.assertEqual( True, self._call_compare('1950-01-01 10:00:00', '1950-01-01 10:00:00', 'eq') )
    self.assertEqual( False, self._call_compare('1950-01-01 10:00:00', '1950-01-01 10:00:01', 'eq') )
    
  def test_compare_ne(self):
    self.assertEqual( False, self._call_compare('1950-01-01 10:00:00', '1950-01-01 10:00:00', 'ne') )
    self.assertEqual( True, self._call_compare('1950-01-01 10:00:00', '1950-01-01 10:00:01', 'ne') )

  def test_compare_lt(self):
    self.assertEqual( True, self._call_compare('1950-01-01 10:00:00', '1950-01-01 10:00:01', 'lt') )
    self.assertEqual( False, self._call_compare('1950-01-01 10:00:00', '1950-01-01 10:00:00', 'lt') )
    self.assertEqual( False, self._call_compare('1950-01-01 10:00:01', '1950-01-01 10:00:00', 'lt') )

  def test_compare_let(self):
    self.assertEqual( True, self._call_compare('1950-01-01 10:00:00', '1950-01-01 10:00:01', 'le') )
    self.assertEqual( True, self._call_compare('1950-01-01 10:00:00', '1950-01-01 10:00:00', 'le') )
    self.assertEqual( False, self._call_compare('1950-01-01 10:00:01', '1950-01-01 10:00:00', 'le') )

  def test_compare_gt(self):
    self.assertEqual( False, self._call_compare('1950-01-01 10:00:00', '1950-01-01 10:00:01', 'gt') )
    self.assertEqual( False, self._call_compare('1950-01-01 10:00:00', '1950-01-01 10:00:00', 'gt') )
    self.assertEqual( True, self._call_compare('1950-01-01 10:00:01', '1950-01-01 10:00:00', 'gt') )
    
  def test_compare_ge(self):
    self.assertEqual( False, self._call_compare('1950-01-01 10:00:00', '1950-01-01 10:00:01', 'ge') )
    self.assertEqual( True, self._call_compare('1950-01-01 10:00:00', '1950-01-01 10:00:00', 'ge') )
    self.assertEqual( True, self._call_compare('1950-01-01 10:00:01', '1950-01-01 10:00:00', 'ge') )
    
if __name__ == '__main__':
  unit_test.main()

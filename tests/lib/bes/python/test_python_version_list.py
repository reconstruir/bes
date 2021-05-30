#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.python.python_version import python_version
from bes.python.python_version_list import python_version_list

class test_python_version_list(unit_test):

  def test_sort(self):
    self.assertEqual( self._make_list( '1.2.1 1.2.2 1.2.10'),
                      self._make_sorted_list('1.2.1 1.2.10 1.2.2') )

  def test_sort_reversed(self):
    self.assertEqual( self._make_list( '1.2.10 1.2.2 1.2.1'),
                      self._make_sorted_list('1.2.1 1.2.10 1.2.2', reverse = True) )
    
  def test_filter_by_version(self):
    self.assertEqual( self._make_list('1.2.1 1.2.2 1.2.10'),
                      self._make_filter_list('1.2.1 1.2.10 1.2.2 1.3.1 1.3.2 1.4.9', '1.2') )

  def test_filter_by_version_no_match(self):
    self.assertEqual( self._make_list(''),
                      self._make_filter_list('1.2.1 1.2.10 1.2.2 1.3.1 1.3.2 1.4.9', '9.9') )
    
  def test_filter_by_full_version(self):
    self.assertEqual( self._make_list('1.2.2'),
                      self._make_filter_list('1.2.1 1.2.10 1.2.2 1.3.1 1.3.2 1.4.9', '1.2.2') )

  def test_filter_by_major_version(self):
    self.assertEqual( self._make_list('1.2.1 1.2.10'),
                      self._make_filter_list('1.2.1 1.2.10 2.1.1 3.4.5 5.6.7', '1') )

  def test__make_version_map(self):
    self.assertEqual( {
      '1.2': [ '1.2.1', '1.2.10' ],
      '2.1': [ '2.1.1' ],
      '3.4': [ '3.4.5' ],
      '5.6': [ '5.6.7' ],
    }, self._make_list('1.2.1 1.2.10 2.1.1 3.4.5 5.6.7')._make_version_map() )

  def test_make_availability_list(self):
    self.assertEqual( [
      '1.2.11',
      '2.1.5',
      '3.4.5',
      '4.6.7',
    ], self._make_list('1.2.1 1.2.10 1.2.11 2.1.1 2.1.4 2.1.5 3.4.5 4.6.7').make_availability_list(1) )

    self.assertEqual( [
      '1.2.10',
      '1.2.11',
      '2.1.4',
      '2.1.5',
      '3.4.5',
      '4.6.7',
    ], self._make_list('1.2.1 1.2.10 1.2.11 2.1.1 2.1.4 2.1.5 3.4.5 4.6.7').make_availability_list(2) )
    
  @classmethod                      
  def _make_sorted_list(clazz, s, reverse = False):
    l = clazz._make_list(s)
    l.sort(reverse = reverse)
    return l

  @classmethod                      
  def _make_list(clazz, s):
    parts = [ p for p in s.split(' ') if p ]
    return python_version_list([ python_version(p) for p in parts ])

  @classmethod                      
  def _make_filter_list(clazz, s, v):
    l = clazz._make_list(s)
    return l.filter_by_version(python_version(v))

  @classmethod                      
  def _make_filter_by_major_version_list(clazz, s, v):
    l = clazz._make_list(s)
    return l.filter_by_major_version(python_version(v))
  
if __name__ == '__main__':
  unit_test.main()

#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.version.semantic_version import semantic_version
from bes.version.semantic_version_list import semantic_version_list

class test_semantic_version_list(unit_test):

  def test_sort(self):
    self.assertEqual( self._make_list( '1.2.1 1.2.2 1.2.10'),
                      self._make_sorted_list('1.2.1 1.2.10 1.2.2') )

  def test_sort_reversed(self):
    self.assertEqual( self._make_list( '1.2.10 1.2.2 1.2.1'),
                      self._make_sorted_list('1.2.1 1.2.10 1.2.2', reverse = True) )
    
  @classmethod                      
  def _make_sorted_list(clazz, s, reverse = False):
    l = clazz._make_list(s)
    l.sort(reverse = reverse)
    return l

  @classmethod                      
  def _make_list(clazz, s):
    parts = [ p for p in s.split(' ') if p ]
    return semantic_version_list([ semantic_version(p) for p in parts ])
  
if __name__ == '__main__':
  unit_test.main()

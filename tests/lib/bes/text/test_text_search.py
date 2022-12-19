#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import OrderedDict
from bes.text.text_search import text_search
from bes.testing.unit_test import unit_test

class test_text_search(unit_test):

  def test_find_all(self):
    self.assertEqual( [
      ( 0, 2 ),
      ( 12, 14 ),
      ( 20, 22 ),
    ], text_search.find_all('foo and bar foo and foo', 'foo') )

  def test_find_all_with_limit(self):
    self.assertEqual( [
      ( 0, 2 ),
    ], text_search.find_all('foo and bar foo and foo', 'foo', limit = 1) )
    
  def test_find_all_word_boundary(self):
    self.assertEqual( [
      ( 12, 14 ),
    ], text_search.find_all('foo1and bar foo and fooy', 'foo', word_boundary = True) )

  def test_rfind_span(self):
    self.assertEqual( ( 13, 17 ), text_search.rfind_span('.png this foo.png', '.png') )
    self.assertEqual( None, text_search.rfind_span('this foo.png', '.jpg') )
    self.assertEqual( None, text_search.rfind_span('this foo.png', '') )
    
if __name__ == '__main__':
  unit_test.main()

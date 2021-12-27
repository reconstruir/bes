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

  def test_find_all_word_boundary(self):
    self.assertEqual( [
      ( 12, 14 ),
    ], text_search.find_all('foo1and bar foo and fooy', 'foo', word_boundary = True) )

if __name__ == '__main__':
  unit_test.main()

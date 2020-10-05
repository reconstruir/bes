#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.match.matcher_util import matcher_util

class TestMatcher(unit_test):

  __TEST_FILENAMES = [
    '/foo/bar/good.txt',
    '/foo/bar/bad.txt',
    '/fruits/apple/apple.png',
    '/fruits/apple/apple2.png',
    '/fruits/orange/orange.png',
    '/fruits/orange/orange2.png',
  ]
  
  def test_match_filenames_include(self):
    include = [
      '/foo*',
    ]
    exclude = None
    matcher_util.match_filenames(self.__TEST_FILENAMES, include, exclude)
    self.assertEqual( [
      '/foo/bar/good.txt',
      '/foo/bar/bad.txt',
    ], matcher_util.match_filenames(self.__TEST_FILENAMES, include, exclude) )

  def test_match_filenames_exclude(self):
    include = None
    exclude = [
      '/fruits*',
    ]
    matcher_util.match_filenames(self.__TEST_FILENAMES, include, exclude)
    self.assertEqual( [
      '/foo/bar/good.txt',
      '/foo/bar/bad.txt',
    ], matcher_util.match_filenames(self.__TEST_FILENAMES, include, exclude) )

  def test_match_filenames_include_exclude(self):
    include = [
      '/foo*',
    ]
    exclude = [
      '*bad*',
    ]
    matcher_util.match_filenames(self.__TEST_FILENAMES, include, exclude)
    self.assertEqual( [
      '/foo/bar/good.txt',
    ], matcher_util.match_filenames(self.__TEST_FILENAMES, include, exclude) )

  def test_match_filenames_both_none(self):
    self.assertEqual( self.__TEST_FILENAMES, matcher_util.match_filenames(self.__TEST_FILENAMES, None, None) )

if __name__ == "__main__":
  unit_test.main()

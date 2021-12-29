#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.text.word_boundary import word_boundary
from bes.testing.unit_test import unit_test

class test_word_boundary(unit_test):

  def test_word_has_boundary(self):
    self.assertEqual( True, word_boundary.word_has_boundary('this is foo', 8, 10) )
    self.assertEqual( False, word_boundary.word_has_boundary('this isafoo', 8, 10) )
    self.assertEqual( False, word_boundary.word_has_boundary('this is_foo', 8, 10) )
    
  def test_word_has_boundary_with_underscore(self):
    self.assertEqual( True, word_boundary.word_has_boundary('this is foo', 8, 10, boundary_chars = word_boundary.CHARS_UNDERSCORE) )
    self.assertEqual( False, word_boundary.word_has_boundary('this isafoo', 8, 10, boundary_chars = word_boundary.CHARS_UNDERSCORE) )
    self.assertEqual( True, word_boundary.word_has_boundary('this is_foo', 8, 10, boundary_chars = word_boundary.CHARS_UNDERSCORE) )
    
  def test_word_has_boundary_with_custom_chars(self):
    self.assertEqual( False, word_boundary.word_has_boundary('a foo', 2, 4, boundary_chars = set('#_@')) )
    self.assertEqual( True, word_boundary.word_has_boundary('a#foo', 2, 4, boundary_chars = set('#_@')) )
    self.assertEqual( False, word_boundary.word_has_boundary('a#foo)', 2, 4, boundary_chars = set('#_@')) )
    self.assertEqual( True, word_boundary.word_has_boundary('a#foo@', 2, 4, boundary_chars = set('#_@')) )
    
if __name__ == '__main__':
  unit_test.main()

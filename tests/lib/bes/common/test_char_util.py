#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.common.char_util import char_util as char_util

class test_char_util(unit_test):

  def test_is_word_boundary(self):
    self.assertEqual( False, char_util.is_word_boundary('a') )
    self.assertEqual( False, char_util.is_word_boundary('z') )
    self.assertEqual( False, char_util.is_word_boundary('A') )
    self.assertEqual( False, char_util.is_word_boundary('Z') )
    self.assertEqual( False, char_util.is_word_boundary('_') )
    self.assertEqual( False, char_util.is_word_boundary('1') )
    self.assertEqual( True, char_util.is_word_boundary('.') )
    self.assertEqual( True, char_util.is_word_boundary('#') )
    self.assertEqual( True, char_util.is_word_boundary(' ') )
    self.assertEqual( True, char_util.is_word_boundary('\t') )
    self.assertEqual( True, char_util.is_word_boundary('\n') )
    
  def test_is_word_boundary_underscore(self):
    self.assertEqual( False, char_util.is_word_boundary('a', underscore = True) )
    self.assertEqual( False, char_util.is_word_boundary('z', underscore = True) )
    self.assertEqual( False, char_util.is_word_boundary('A', underscore = True) )
    self.assertEqual( False, char_util.is_word_boundary('Z', underscore = True) )
    self.assertEqual( True, char_util.is_word_boundary('_', underscore = True) )
    self.assertEqual( False, char_util.is_word_boundary('1', underscore = True) )
    self.assertEqual( True, char_util.is_word_boundary('.', underscore = True) )
    self.assertEqual( True, char_util.is_word_boundary('#', underscore = True) )
    self.assertEqual( True, char_util.is_word_boundary(' ') )
    self.assertEqual( True, char_util.is_word_boundary('\t') )
    self.assertEqual( True, char_util.is_word_boundary('\n') )
    
if __name__ == '__main__':
  unit_test.main()

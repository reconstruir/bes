#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.text.text_levenshtein import text_levenshtein

class test_text_levenshtein(unit_test):

  def test_distance(self):
    self.assertEqual( 1, text_levenshtein.distance('foo', 'food') )
    self.assertEqual( 1, text_levenshtein.distance('food', 'foo') )
    self.assertEqual( 3, text_levenshtein.distance('foo', 'foodie') )
    self.assertEqual( 1, text_levenshtein.distance('reod', 'read') )
    
if __name__ == '__main__':
  unit_test.main()

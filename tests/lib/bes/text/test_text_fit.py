#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import unittest
from bes.text.text_fit import text_fit

class test_text_fit(unittest.TestCase):

  def test_fit(self):
    self.assertEqual( [ 'foo bar', 'baz', 'something' ], text_fit.fit_line('foo bar baz something', 10) )
    self.assertEqual( [ 'foo bar baz', 'something' ], text_fit.fit_line('foo bar baz something', 12) )
    self.assertEqual( [ 'foo  bar', 'baz', 'something' ], text_fit.fit_line('foo  bar baz something', 10) )
    self.assertEqual( [ 'foo  bar', 'baz', 'something' ], text_fit.fit_line('foo  bar  baz something', 10) )
    self.assertEqual( [ 'foo  bar', 'baz  kiwi' ], text_fit.fit_line('foo  bar  baz  kiwi', 12) )
  
if __name__ == '__main__':
  unittest.main()

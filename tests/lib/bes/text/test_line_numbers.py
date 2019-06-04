#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import unittest
from bes.text.line_numbers import line_numbers

class test_line_numbers(unittest.TestCase):

  def test_fit(self):
    self.assertEqual(
      '''1|foo
2|bar
3|
''',
      line_numbers.add_line_numbers('foo\nbar\n') )
  
if __name__ == '__main__':
  unittest.main()

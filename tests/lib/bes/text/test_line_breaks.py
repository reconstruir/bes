#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import unittest
from bes.text.line_breaks import line_breaks

class test_line_breaks(unittest.TestCase):

  def test_fit(self):
    self.assertFalse( line_breaks.ends_with_line_break('foo') )
    self.assertTrue( line_breaks.ends_with_line_break('foo\n') )
    self.assertTrue( line_breaks.ends_with_line_break('foo\r') )
    self.assertTrue( line_breaks.ends_with_line_break('foo\n\r') )
    self.assertTrue( line_breaks.ends_with_line_break('foo\r\n') )
  
if __name__ == '__main__':
  unittest.main()

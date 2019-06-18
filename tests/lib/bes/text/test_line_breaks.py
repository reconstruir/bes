#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import unittest
from bes.text.line_breaks import line_breaks

class test_line_breaks(unittest.TestCase):

  def test_ends_with_line_break(self):
    self.assertFalse( line_breaks.ends_with_line_break('foo') )
    self.assertTrue( line_breaks.ends_with_line_break('foo\n') )
    self.assertTrue( line_breaks.ends_with_line_break('foo\r') )
    self.assertTrue( line_breaks.ends_with_line_break('foo\n\r') )
    self.assertTrue( line_breaks.ends_with_line_break('foo\r\n') )

  def test_is_line_break(self):
    self.assertFalse( line_breaks.is_line_break('') )
    self.assertFalse( line_breaks.is_line_break('a') )
    self.assertTrue( line_breaks.is_line_break('\n') )
    self.assertTrue( line_breaks.is_line_break('\r') )
    self.assertFalse( line_breaks.is_line_break('\n\r') )
    self.assertTrue( line_breaks.is_line_break('\r\n') )
    
if __name__ == '__main__':
  unittest.main()

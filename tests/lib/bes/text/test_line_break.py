#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import unittest
from bes.text.line_break import line_break

class test_line_break(unittest.TestCase):

  def test_ends_with_line_break(self):
    self.assertFalse( line_break.ends_with_line_break('foo') )
    self.assertTrue( line_break.ends_with_line_break('foo\n') )
    self.assertTrue( line_break.ends_with_line_break('foo\r') )
    self.assertTrue( line_break.ends_with_line_break('foo\n\r') )
    self.assertTrue( line_break.ends_with_line_break('foo\r\n') )

  def test_is_line_break(self):
    self.assertFalse( line_break.is_line_break('') )
    self.assertFalse( line_break.is_line_break('a') )
    self.assertTrue( line_break.is_line_break('\n') )
    self.assertTrue( line_break.is_line_break('\r') )
    self.assertFalse( line_break.is_line_break('\n\r') )
    self.assertTrue( line_break.is_line_break('\r\n') )
    
  def test_guess_line_break(self):
    self.assertEqual( '\n', line_break.guess_line_break('foo\nbar') )
    self.assertEqual( '\r\n', line_break.guess_line_break('foo\r\nbar') )
    self.assertEqual( '\n', line_break.guess_line_break('foo\n\rbar') )
    self.assertEqual( '\r\n', line_break.guess_line_break('foo\r\nbar\nbaz') )
    self.assertEqual( '\r\n', line_break.guess_line_break('foo\nbar\r\nbaz') )
    
if __name__ == '__main__':
  unittest.main()

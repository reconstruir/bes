#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.text import white_space as WS

class test_white_space(unit_test):

  def test_count_leading_spaces(self):
    self.assertEqual( 2, WS.count_leading_spaces('  a b c') )
    
  def test_escape_white_space(self):
    self.assertEqual( 'foo\\ bar', WS.escape_white_space('foo bar') )
    self.assertEqual( 'foo\\ bar', WS.escape_white_space('foo\\ bar') )
    self.assertEqual( 'foo\\\nbar', WS.escape_white_space('foo\nbar') )
    self.assertEqual( 'foo\\\tbar', WS.escape_white_space('foo\tbar') )
    
if __name__ == "__main__":
  unit_test.main()

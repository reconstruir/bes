#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.text.white_space import white_space as WS

class test_white_space(unit_test):

  def test_count_leading_spaces(self):
    self.assertEqual( 2, WS.count_leading_spaces('  a b c') )
    
  def test_escape_white_space(self):
    self.assertEqual( 'foo\\ bar', WS.escape_white_space('foo bar') )
    self.assertEqual( 'foo\\ bar', WS.escape_white_space('foo\\ bar') )
    self.assertEqual( 'foo\\\nbar', WS.escape_white_space('foo\nbar') )
    self.assertEqual( 'foo\\\tbar', WS.escape_white_space('foo\tbar') )
    
  def test_strip_head_new_lines(self):
    self.assertEqual( '', WS.strip_head_new_lines('') )
    self.assertEqual( '', WS.strip_head_new_lines('\n') )
    self.assertEqual( '', WS.strip_head_new_lines('\n\n') )
    self.assertEqual( 'foo', WS.strip_head_new_lines('\nfoo') )
    self.assertEqual( 'foo\n', WS.strip_head_new_lines('\nfoo\n') )
    self.assertEqual( 'foo\n', WS.strip_head_new_lines('foo\n') )
    
  def test_strip_tail_new_lines(self):
    self.assertEqual( '', WS.strip_tail_new_lines('') )
    self.assertEqual( '', WS.strip_tail_new_lines('\n') )
    self.assertEqual( '', WS.strip_tail_new_lines('\n\n') )
    self.assertEqual( 'foo', WS.strip_tail_new_lines('foo\n') )
    self.assertEqual( '\nfoo', WS.strip_tail_new_lines('\nfoo') )
    self.assertEqual( '\nfoo', WS.strip_tail_new_lines('\nfoo\n') )
    
  def test_strip_new_lines(self):
    self.assertEqual( '', WS.strip_new_lines('') )
    self.assertEqual( '', WS.strip_new_lines('\n') )
    self.assertEqual( '', WS.strip_new_lines('\n\n') )
    self.assertEqual( 'foo', WS.strip_new_lines('foo\n') )
    self.assertEqual( 'foo', WS.strip_new_lines('\nfoo') )
    self.assertEqual( 'foo', WS.strip_new_lines('\nfoo\n') )
    
if __name__ == "__main__":
  unit_test.main()

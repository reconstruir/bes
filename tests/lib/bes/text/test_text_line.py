#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test

from bes.text.text_line import text_line as TL

class test_text_line(unit_test):

  def test_text_no_comments(self):
    self.assertEqual( 'foo', TL(1, 'foo#comment').text_no_comments )
    
  def test_clone_stripped(self):
    self.assertEqual( ( 1, 'foo' ), TL(1, '  foo  ').clone_stripped() )
    
  def test_clone_line_number(self):
    self.assertEqual( ( 2, 'foo' ), TL(1, 'foo').clone_line_number(2) )
    
  def test_expand_continuations(self):
    self.assertEqual( [ TL(1, 'foo' ), TL(2, 'bar') ], TL(1, 'foo\\bar').expand_continuations() )
    
  def test_expand_continuations_with_indent(self):
    self.assertEqual( [ TL(1, 'foo' ), TL(2, 'bar') ], TL(1, 'foo\\bar').expand_continuations(indent = 0) )
    self.assertEqual( [ TL(1, 'foo' ), TL(2, ' bar') ], TL(1, 'foo\\bar').expand_continuations(indent = 1) )
    self.assertEqual( [ TL(1, 'foo' ) ], TL(1, 'foo').expand_continuations(indent = 1) )
    self.assertEqual( [ TL(1, 'foo' ), TL(2, '  bar') ], TL(1, 'foo\\bar').expand_continuations(indent = 2) )
    self.assertEqual( [ TL(1, 'foo' ), TL(2, '  bar'), TL(3, '  baz') ], TL(1, 'foo\\bar\\baz').expand_continuations(indent = 2) )
    
if __name__ == '__main__':
  unit_test.main()

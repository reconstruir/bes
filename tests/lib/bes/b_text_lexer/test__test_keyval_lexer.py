#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test

from _test_keyval_lexer import _test_keyval_lexer

class test__test_keyval_lexer(unit_test):

  def test_tokenize(self):
    l = _test_keyval_lexer()
    text = '''
fruit=kiwi
'''
    self.assertEqual( [
      ( 't_line_break', '', (1, 1) ),
      ( 't_key', 'fruit', (1, 2) ),
      ( 't_value', 'kiwi', (1, 2) ),
      ( 't_line_break', '', (1, 2) ),
      ( 't_done', '', (1, 3) ),
    ], l.tokenize(text) )

if __name__ == '__main__':
  unit_test.main()

#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test

from _test_keyval_lexer import _test_keyval_lexer

class test__test_keyval_lexer(unit_test):

  def test_tokenize(self):
    l = _test_keyval_lexer()
    text = 'a=b'
    actual = l.tokenize(text).to_json()
    #print(actual)
    #return
    self.assert_string_equal_fuzzy( '''
[
  {
    "name": "t_key", 
    "value": "a", 
    "position": "1,1"
  }, 
  {
    "name": "t_equal", 
    "value": "", 
    "position": "1,1"
  }, 
  {
    "name": "t_value", 
    "value": "b", 
    "position": "1,1"
  }, 
  {
    "name": "t_done", 
    "value": "", 
    "position": "1,1"
  }
]
''', actual )

  def xtest_tokenize_with_line_breaks(self):
    l = _test_keyval_lexer()
    text = '''
fruit=kiwi
'''
    #actual = l.tokenize(text).to_json()
    #print(actual)
    return
    self.assert_string_equal_fuzzy( '''
[
  {
    "name": "t_line_break", 
    "value": "", 
    "position": {
      "x": 1, 
      "y": 1
    }
  }, 
  {
    "name": "t_key", 
    "value": "fruit", 
    "position": {
      "x": 1, 
      "y": 2
    }
  }, 
  {
    "name": "t_value", 
    "value": "kiwi", 
    "position": {
      "x": 1, 
      "y": 2
    }
  }, 
  {
    "name": "t_line_break", 
    "value": "", 
    "position": {
      "x": 1, 
      "y": 2
    }
  }, 
  {
    "name": "t_done", 
    "value": "", 
    "position": {
      "x": 1, 
      "y": 3
    }
  }
]
''', actual )
    
if __name__ == '__main__':
  unit_test.main()

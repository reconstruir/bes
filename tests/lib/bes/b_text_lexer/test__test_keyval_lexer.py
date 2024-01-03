#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test

from bes.b_text_lexer.btl_lexer_token_list import btl_lexer_token_list

from _test_keyval_lexer import _test_keyval_lexer

class test__test_keyval_lexer(unit_test):

  def test_empty_string(self):
    self._test('',
      [
        ( 't_done', '', ( 1, 1 ) ),
      ])

  def test_just_key(self):
    self._test('a',
      [
        ( 't_key', 'a', ( 1, 1 ) ),
        ( 't_done', '', ( 2, 1 ) ),
      ])
    
  def test_just_key_and_equal(self):
    self._test('ab=',
      [
        ( 't_key', 'ab', ( 1, 1 ) ),
        ( 't_equal', '=', ( 3, 1 ) ),
        ( 't_value', '', ( 3, 1 ) ),
        ( 't_done', '', ( 4, 1 ) ),
      ])

  def test_key_and_value(self):
    self._test('a=k',
      [
        ( 't_key', 'a', ( 1, 1 ) ),
        ( 't_equal', '=', ( 2, 1 ) ),
        ( 't_value', 'k', ( 3, 1 ) ),
        ( 't_done', '', ( 4, 1 ) ),
      ])

  def test_key_and_value(self):
    self._test('fruit=kiwi',
      [
        ( 't_key', 'fruit', ( 1, 1 ) ),
        ( 't_equal', '=', ( 6, 1 ) ),
        ( 't_value', 'kiwi', ( 7, 1 ) ),
        ( 't_done', '', ( 11, 1 ) ),
      ])

  def test_multi_line(self):
    self._test('''fruit=kiwi
color=green
''', 
      [
#        ( 't_line_break', '', ( 1, 1 ) ),
        ( 't_key', 'fruit', ( 1, 1 ) ),
        ( 't_equal', '=', ( 6, 1 ) ),
        ( 't_value', 'kiwi', ( 7, 1 ) ),
        ( 't_line_break', '', ( 11, 1 ) ),
        ( 't_key', 'color', ( 1, 2 ) ),
        ( 't_equal', '=', ( 6, 2 ) ),
        ( 't_value', 'green', ( 7, 2 ) ),
        ( 't_line_break', '', ( 12, 2 ) ),
        ( 't_done', '', ( 1, 3 ) ),
      ])
    
  def xtest_tokenize(self):
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


  def _test(self, text, expected):
    actual_tokens = _test_keyval_lexer().tokenize(text)
    actual_json = actual_tokens.to_json()
    expected_tokens = btl_lexer_token_list(expected)
    expected_json = btl_lexer_token_list(expected).to_json()

    expected_string = '\n'.join([ str(token) for token in expected_tokens ])
    actual_string = '\n'.join([ str(token) for token in actual_tokens ])

    if self.DEBUG:
      for i, token in enumerate(actual_tokens, start = 1):
        print(f'{i}: {token}', flush = True)
      
    self.assertMultiLineEqual( expected_string, actual_string )
    
if __name__ == '__main__':
  unit_test.main()

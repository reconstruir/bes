#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import unittest
from bes.text import string_lexer as L

T = L.token
COMMENT = L.TOKEN_COMMENT
DONE = L.TOKEN_DONE
SPACE = L.TOKEN_SPACE
STRING = L.TOKEN_STRING

def TSPACE(line_number): return T(SPACE, ' ', line_number)
def TDONE(line_number): return T(DONE, None, line_number)

class test_string_lexer(unittest.TestCase):

  def test_empty_string(self):
    self.assertEqual( [ TDONE(1) ],
                      self.__tokenize(r'') )

  def test_single_char(self):
    self.assertEqual( [ (STRING, 'a', 1), TDONE(1) ],
                      self.__tokenize(r'a') )
    
  def test_one_escape(self):
    self.assertEqual( [ (STRING, 'a', 1), TDONE(1) ],
                      self.__tokenize(r'\a') )
    
  def test_escape_backslash(self):
    self.assertEqual( [ (STRING, r'\a', 1), TDONE(1) ],
                      self.__tokenize(r'\\a') )

  def test_eos_when_escaping(self):
    self.assertEqual( [ (STRING, 'a', 1), TDONE(1) ],
                      self.__tokenize('a\\') )
    
  def test_simple(self):
    self.maxDiff = None
    self.assertEqual( [ TSPACE(1), (STRING, 'foo', 1), TSPACE(1), TDONE(1) ],
                      self.__tokenize(r' foo ') )
    
    self.assertEqual( [ TSPACE(1), (STRING, 'foo', 1), TSPACE(1), (STRING, '=', 1), TSPACE(1), (STRING, '123', 1), (SPACE, '  ', 1), TDONE(1) ],
                      self.__tokenize(r' foo = 123  ') )

    self.assertEqual( [ TSPACE(1), (STRING, 'foo=', 1), TSPACE(1), (STRING, '123', 1), (SPACE, '  ', 1), TDONE(1) ],
                      self.__tokenize(r' foo= 123  ') )

    self.assertEqual( [ TSPACE(1), (STRING, 'foo=123', 1), (SPACE, '  ', 1), TDONE(1) ],
                      self.__tokenize(r' foo=123  ') )

    self.assertEqual( [ TSPACE(1), (STRING, 'foo=123', 1), TDONE(1) ],
                      self.__tokenize(r' foo=123') )

    self.assertEqual( [ (STRING, 'foo=123', 1), TDONE(1) ],
                      self.__tokenize(r'foo=123') )
    self.assertEqual( [ (STRING, 'a', 1), TSPACE(1), (STRING, 'b', 1), TDONE(1) ],
                      self.__tokenize(r'a b') )

  def test_quote(self):
    self.assertEqual( [ (STRING, 'a b', 1), TDONE(1) ],
                      self.__tokenize(r'"a b"') )
    self.assertEqual( [ TSPACE(1), (STRING, 'foo bar', 1), TSPACE(1), (STRING, 'a b c', 1), TSPACE(1), TDONE(1) ],
                      self.__tokenize(r' "foo bar" "a b c" ') )
    self.assertEqual( [ TSPACE(1), (STRING, 'foo bar', 1), (STRING, 'a b c', 1), TSPACE(1), TDONE(1) ],
                      self.__tokenize(r' "foo bar""a b c" ') )
    self.assertEqual( [ (STRING, 'foo bar', 1), (STRING, 'a b c', 1), TSPACE(1), TDONE(1) ],
                      self.__tokenize(r'"foo bar""a b c" ') )
    self.assertEqual( [ (STRING, 'foo bar', 1), (STRING, 'a b c', 1), TDONE(1) ],
                      self.__tokenize(r'"foo bar""a b c"') )
    
  def test_single_quote_escaped_within_quotes(self):
    self.assertEqual( [ (STRING, 'a " b', 1), TDONE(1) ],
                      self.__tokenize(r'"a \" b"') )
    self.assertEqual( [ (STRING, 'a \' b', 1), TDONE(1) ],
                      self.__tokenize(r'"a \' b"') )
    self.assertEqual( [ (STRING, 'a " b', 1), TDONE(1) ],
                      self.__tokenize(r"'a \" b'") )
    self.assertEqual( [ (STRING, 'a \' b', 1), TDONE(1) ],
                      self.__tokenize(r"'a \' b'") )

  def test_escaped_spaces(self):
    self.assertEqual( [ (STRING, 'a b', 1), TDONE(1) ],
                      self.__tokenize(r'a\ b') )
    self.assertEqual( [ (STRING, 'foo=a b', 1), TDONE(1) ],
                      self.__tokenize(r'foo=a\ b') )
    self.assertEqual( [ (STRING, 'fo o=a b', 1), TDONE(1) ],
                      self.__tokenize(r'fo\ o=a\ b') )

  def test_comment(self):
    self.assertEqual( [ (STRING, 'a=1', 1), TSPACE(1), (COMMENT, '# hi', 1), TDONE(1) ],
                      self.__tokenize(r'a=1 # hi') )
    self.assertEqual( [ (STRING, 'a=1', 1), (COMMENT, '# hi', 1), TDONE(1) ],
                      self.__tokenize(r'a=1# hi') )
    self.assertEqual( [ (COMMENT, '# hi', 1), TDONE(1) ],
                      self.__tokenize(r'# hi') )
    self.assertEqual( [ TSPACE(1), (COMMENT, '# hi', 1), TDONE(1) ],
                      self.__tokenize(r' # hi') )
    self.assertEqual( [ (STRING, 'a=', 1),TSPACE(1), (COMMENT, '# hi', 1), TDONE(1) ],
                      self.__tokenize(r'a= # hi') )
    self.assertEqual( [ (STRING, 'a=', 1), (COMMENT, '# hi', 1), TDONE(1) ],
                      self.__tokenize(r'a=# hi') )
  def test_quoted_string_inside_string(self):
    self.assertEqual( [ (STRING, 'af o o', 1), TDONE(1) ],
                      self.__tokenize(r'a"f o o"') )

  def test_escaped_quote_string_inside_string(self):
    self.assertEqual( [ (STRING, r"a='foo'", 1), TDONE(1) ],
                      self.__tokenize(r'a=\'foo\'') )
    self.assertEqual( [ (STRING, 'a=', 1), TSPACE(1), (STRING, r"'foo'", 1), TDONE(1) ],
                      self.__tokenize(r'a= \'foo\'') )

  def test_escaped_equal_inside_string(self):
    self.assertEqual( [ (STRING, 'a==b', 1), TDONE(1) ],
                      self.__tokenize(r'a\==b') )
    self.assertEqual( [ (STRING, '=a=b', 1), TDONE(1) ],
                      self.__tokenize(r'\=a=b') )
    self.assertEqual( [ (STRING, 'a=b=', 1), TDONE(1) ],
                      self.__tokenize(r'a=b\=') )

  def test_escaped_space_inside_string(self):
    self.assertEqual( [ (STRING, 'a =b', 1), TDONE(1) ],
                      self.__tokenize(r'a\ =b') )
    self.assertEqual( [ (STRING, ' a=b', 1), TDONE(1) ],
                      self.__tokenize(r'\ a=b') )
    self.assertEqual( [ (STRING, 'a=b ', 1), TDONE(1) ],
                      self.__tokenize(r'a=b\ ') )

  def xtest_delimiter_is_none(self):
    self.assertEqual( [ (STRING, 'a =b', 1), TDONE(1) ],
                      self.__tokenize(r'a\ =b', delimiter = None) )
    self.assertEqual( [ (STRING, 'a=b', 1), TDONE(1) ],
                      self.__tokenize(r'a=b', delimiter = None) )
    self.assertEqual( [ (STRING, 'a', 1), TSPACE(1), (STRING, '=b', 1), TDONE(1) ],
                      self.__tokenize(r'a =b', delimiter = None) )
    self.assertEqual( [ (STRING, 'a', 1), TSPACE(1), (STRING, '=', 1), TSPACE(1), (STRING, 'b', 1), TDONE(1) ],
                      self.__tokenize(r'a = b', delimiter = None) )

  def test_new_line(self):
    self.assertEqual( [ (STRING, 'a=foo', 1), (SPACE, ' \n ', 2), (STRING, 'b=bar', 2), T(DONE, None, 2) ],
                      self.__tokenize('a=foo \n b=bar') )

  def test_escaped_new_line(self):
    self.assertEqual( [ (STRING, 'a=f\no', 2), T(DONE, None, 2) ],
                      self.__tokenize('a=f\\\no') )

  def test_keep_quotes(self):
    self.assertEqual( [ (STRING, 'a=foo bar baz', 1), TDONE(1) ],
                      self.__tokenize(r'a="foo bar baz"') )
    self.assertEqual( [ (STRING, 'a="foo bar baz"', 1), TDONE(1) ],
                      self.__tokenize(r'a="foo bar baz"', keep_quotes = True) )

  def test_keep_quotes_escaped(self):
    self.assertEqual( [ (STRING, 'a=foo bar baz', 1), TDONE(1) ],
                      self.__tokenize(r'a="foo bar baz"') )
    self.assertEqual( [ (STRING, 'a=\\"foo bar baz\\"', 1), TDONE(1) ],
                      self.__tokenize(r'a="foo bar baz"', keep_quotes = True, escape_quotes = True) )

  def test_line_numbers(self):
    '''
    1: a=5
    2: b=6
    3: 
    4: c=7
    5:
    '''
    self.assertEqual( [ (STRING, 'a=5', 1), (SPACE, '\n', 2), 
                        (STRING, 'b=6', 2), (SPACE, '\n\n', 4),
                        (STRING, 'c=7', 4), (SPACE, '\n', 5), 
                        TDONE(5) ],
                      self.__tokenize('a=5\nb=6\n\nc=7\n') )

  @classmethod
  def __tokenize(self, text, delimiter = '=',
                 keep_quotes = False,
                 escape_quotes = False,
                 ignore_comments = False):
    options = 0
    if keep_quotes:
      options |= L.KEEP_QUOTES
    if escape_quotes:
      options |= L.ESCAPE_QUOTES
    if ignore_comments:
      options |= L.IGNORE_COMMENTS
    return [ token for token in L.tokenize(text, delimiter, options = options) ]

  def assertEqual(self, expected, actual):
    assert isinstance(expected, list)
    expected = [ L.token(*t) for t in expected ]
    super(test_string_lexer, self).assertEqual(expected, actual)

if __name__ == "__main__":
  unittest.main()

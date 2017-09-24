#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import unittest
from bes.key_value import key_value_lexer as L

T = L.token
COMMENT = L.TOKEN_COMMENT
DONE = L.TOKEN_DONE
DELIMITER = L.TOKEN_DELIMITER
SPACE = L.TOKEN_SPACE
STRING = L.TOKEN_STRING

def TSPACE(line_number): return T(SPACE, ' ', line_number)
def TDELIMITER(line_number): return T(DELIMITER, '=', line_number)
def TDONE(line_number): return T(DONE, None, line_number)

class test_key_value_lexer(unittest.TestCase):

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
    
    self.assertEqual( [ TSPACE(1), (STRING, 'foo', 1), TSPACE(1), TDELIMITER(1), TSPACE(1), (STRING, '123', 1), (SPACE, '  ', 1), TDONE(1) ],
                      self.__tokenize(r' foo = 123  ') )

    self.assertEqual( [ TSPACE(1), (STRING, 'foo', 1), TDELIMITER(1), TSPACE(1), (STRING, '123', 1), (SPACE, '  ', 1), TDONE(1) ],
                      self.__tokenize(r' foo= 123  ') )

    self.assertEqual( [ TSPACE(1), (STRING, 'foo', 1), TDELIMITER(1), (STRING, '123', 1), (SPACE, '  ', 1), TDONE(1) ],
                      self.__tokenize(r' foo=123  ') )

    self.assertEqual( [ TSPACE(1), (STRING, 'foo', 1), TDELIMITER(1), (STRING, '123', 1), TDONE(1) ],
                      self.__tokenize(r' foo=123') )

    self.assertEqual( [ (STRING, 'foo', 1), TDELIMITER(1), (STRING, '123', 1), TDONE(1) ],
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
    self.assertEqual( [ (STRING, 'foo', 1), TDELIMITER(1), (STRING, 'a b', 1), TDONE(1) ],
                      self.__tokenize(r'foo=a\ b') )
    self.assertEqual( [ (STRING, 'fo o', 1), TDELIMITER(1), (STRING, 'a b', 1), TDONE(1) ],
                      self.__tokenize(r'fo\ o=a\ b') )

  def test_comment(self):
    self.assertEqual( [ (STRING, 'a', 1), TDELIMITER(1), (STRING, '1', 1), TSPACE(1), (COMMENT, '# hi', 1), TDONE(1) ],
                      self.__tokenize(r'a=1 # hi') )
    self.assertEqual( [ (STRING, 'a', 1), TDELIMITER(1), (STRING, '1', 1), (COMMENT, '# hi', 1), TDONE(1) ],
                      self.__tokenize(r'a=1# hi') )
    self.assertEqual( [ (COMMENT, '# hi', 1), TDONE(1) ],
                      self.__tokenize(r'# hi') )
    self.assertEqual( [ TSPACE(1), (COMMENT, '# hi', 1), TDONE(1) ],
                      self.__tokenize(r' # hi') )
    self.assertEqual( [ (STRING, 'a', 1), TDELIMITER(1), TSPACE(1), (COMMENT, '# hi', 1), TDONE(1) ],
                      self.__tokenize(r'a= # hi') )
    self.assertEqual( [ (STRING, 'a', 1), TDELIMITER(1), (COMMENT, '# hi', 1), TDONE(1) ],
                      self.__tokenize(r'a=# hi') )
  def test_quoted_string_inside_string(self):
    self.assertEqual( [ (STRING, 'af o o', 1), TDONE(1) ],
                      self.__tokenize(r'a"f o o"') )

  def test_escaped_quote_string_inside_string(self):
    self.assertEqual( [ (STRING, 'a', 1), TDELIMITER(1), (STRING, r"'foo'", 1), TDONE(1) ],
                      self.__tokenize(r'a=\'foo\'') )
    self.assertEqual( [ (STRING, 'a', 1), TDELIMITER(1), TSPACE(1), (STRING, r"'foo'", 1), TDONE(1) ],
                      self.__tokenize(r'a= \'foo\'') )

  def test_escaped_equal_inside_string(self):
    self.assertEqual( [ (STRING, 'a=', 1), TDELIMITER(1), (STRING, 'b', 1), TDONE(1) ],
                      self.__tokenize(r'a\==b') )
    self.assertEqual( [ (STRING, '=a', 1), TDELIMITER(1), (STRING, 'b', 1), TDONE(1) ],
                      self.__tokenize(r'\=a=b') )
    self.assertEqual( [ (STRING, 'a', 1), TDELIMITER(1), (STRING, 'b=', 1), TDONE(1) ],
                      self.__tokenize(r'a=b\=') )

  def test_escaped_space_inside_string(self):
    self.assertEqual( [ (STRING, 'a ', 1), TDELIMITER(1), (STRING, 'b', 1), TDONE(1) ],
                      self.__tokenize(r'a\ =b') )
    self.assertEqual( [ (STRING, ' a', 1), TDELIMITER(1), (STRING, 'b', 1), TDONE(1) ],
                      self.__tokenize(r'\ a=b') )
    self.assertEqual( [ (STRING, 'a', 1), TDELIMITER(1), (STRING, 'b ', 1), TDONE(1) ],
                      self.__tokenize(r'a=b\ ') )

  def test_new_line(self):
    self.assertEqual( [ (STRING, 'a', 1), TDELIMITER(1), (STRING, 'foo', 1), (SPACE, ' \n ', 2), (STRING, 'b', 2), TDELIMITER(2), (STRING, 'bar', 2), T(DONE, None, 2) ],
                      self.__tokenize('a=foo \n b=bar') )

  def test_escaped_new_line(self):
    self.assertEqual( [ (STRING, 'a', 1), TDELIMITER(1), (STRING, 'f\no', 2), T(DONE, None, 2) ],
                      self.__tokenize('a=f\\\no') )

  def test_keep_quotes(self):
    self.assertEqual( [ (STRING, 'a', 1), TDELIMITER(1), (STRING, 'foo bar baz', 1), TDONE(1) ],
                      self.__tokenize(r'a="foo bar baz"') )
    self.assertEqual( [ (STRING, 'a', 1), TDELIMITER(1), (STRING, '"foo bar baz"', 1), TDONE(1) ],
                      self.__tokenize(r'a="foo bar baz"', keep_quotes = True) )

  def test_keep_quotes_escaped(self):
    self.assertEqual( [ (STRING, 'a', 1), TDELIMITER(1), (STRING, 'foo bar baz', 1), TDONE(1) ],
                      self.__tokenize(r'a="foo bar baz"') )
    self.assertEqual( [ (STRING, 'a', 1), TDELIMITER(1), (STRING, '\\"foo bar baz\\"', 1), TDONE(1) ],
                      self.__tokenize(r'a="foo bar baz"', keep_quotes = True, escape_quotes = True) )

  def test_line_numbers(self):
    '''
    1: a=5
    2: b=6
    3: 
    4: c=7
    5:
    '''
    self.assertEqual( [ (STRING, 'a', 1), TDELIMITER(1), (STRING, '5', 1), (SPACE, '\n', 2), 
                        (STRING, 'b', 2), TDELIMITER(2), (STRING, '6', 2), (SPACE, '\n\n', 4),
#                        (SPACE, '\n\n', 4), 
                        (STRING, 'c', 4), TDELIMITER(4), (STRING, '7', 4), (SPACE, '\n', 5), 
                        TDONE(5) ],
                      self.__tokenize('a=5\nb=6\n\nc=7\n') )

  def xtest_kv_delimiter(self):
    self.assertEqual( [ (STRING, 'a b ', 1), TDELIMITER(1), (STRING, ' 5 6', 1), (SPACE, '\n', 2),
                        (STRING, 'c d  ', 2), TDELIMITER(2), (STRING, ' 7 8', 2), TDONE(2) ],
                      self.__tokenize('a b = 5 6\nc d = 7 8', ignore_spaces = True, kv_delimiters = '\n') )

  @classmethod
  def __tokenize(self, text,
                 delimiter = '=',
                 kv_delimiters = None,
                 keep_quotes = False,
                 escape_quotes = False,
                 ignore_comments = False,
                 ignore_spaces = False):
    options = 0
    if keep_quotes:
      options |= L.KEEP_QUOTES
    if escape_quotes:
      options |= L.ESCAPE_QUOTES
    if ignore_comments:
      options |= L.IGNORE_COMMENTS
    if ignore_spaces:
      options |= L.IGNORE_SPACES
    return [ token for token in L.tokenize(text, delimiter, options = options) ]

  def assertEqual(self, expected, actual):
    assert isinstance(expected, list)
    expected = [ L.token(*t) for t in expected ]
    super(test_key_value_lexer, self).assertEqual(expected, actual)

if __name__ == "__main__":
  unittest.main()

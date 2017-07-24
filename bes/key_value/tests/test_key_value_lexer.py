#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import unittest
from bes.key_value import key_value_lexer as L

T = L.token
COMMENT = L.COMMENT
DONE = L.DONE
DELIMITER = L.DELIMITER
SPACE = L.SPACE
STRING = L.STRING

TDONE = T(DONE, None)
TSPACE = T(SPACE, ' ')
TDELIMITER = T(DELIMITER, '=')

class test_key_value_lexer(unittest.TestCase):

  def test_simple(self):
    self.maxDiff = None
    self.assertEqual( [ TSPACE, (STRING, 'foo'), TSPACE, TDONE ],
                      self.__tokenize(r' foo ') )
    
    self.assertEqual( [ TSPACE, (STRING, 'foo'), TSPACE, TDELIMITER, TSPACE, (STRING, '123'), (SPACE, '  '), TDONE ],
                      self.__tokenize(r' foo = 123  ') )

    self.assertEqual( [ TSPACE, (STRING, 'foo'), TDELIMITER, TSPACE, (STRING, '123'), (SPACE, '  '), TDONE ],
                      self.__tokenize(r' foo= 123  ') )

    self.assertEqual( [ TSPACE, (STRING, 'foo'), TDELIMITER, (STRING, '123'), (SPACE, '  '), TDONE ],
                      self.__tokenize(r' foo=123  ') )

    self.assertEqual( [ TSPACE, (STRING, 'foo'), TDELIMITER, (STRING, '123'), TDONE ],
                      self.__tokenize(r' foo=123') )

    self.assertEqual( [ (STRING, 'foo'), TDELIMITER, (STRING, '123'), TDONE ],
                      self.__tokenize(r'foo=123') )
    self.assertEqual( [ (STRING, 'a'), TSPACE, (STRING, 'b'), TDONE ],
                      self.__tokenize(r'a b') )

  def test_quote(self):
    self.assertEqual( [ (STRING, 'a b'), TDONE ],
                      self.__tokenize(r'"a b"') )
    self.assertEqual( [ TSPACE, (STRING, 'foo bar'), TSPACE, (STRING, 'a b c'), TSPACE, TDONE ],
                      self.__tokenize(r' "foo bar" "a b c" ') )
    self.assertEqual( [ TSPACE, (STRING, 'foo bar'), (STRING, 'a b c'), TSPACE, TDONE ],
                      self.__tokenize(r' "foo bar""a b c" ') )
    self.assertEqual( [ (STRING, 'foo bar'), (STRING, 'a b c'), TSPACE, TDONE ],
                      self.__tokenize(r'"foo bar""a b c" ') )
    self.assertEqual( [ (STRING, 'foo bar'), (STRING, 'a b c'), TDONE ],
                      self.__tokenize(r'"foo bar""a b c"') )
    
  def test_single_quote_escaped_within_quotes(self):
    self.assertEqual( [ (STRING, 'a " b'), TDONE ],
                      self.__tokenize(r'"a \" b"') )
    self.assertEqual( [ (STRING, 'a \' b'), TDONE ],
                      self.__tokenize(r'"a \' b"') )
    self.assertEqual( [ (STRING, 'a " b'), TDONE ],
                      self.__tokenize(r"'a \" b'") )
    self.assertEqual( [ (STRING, 'a \' b'), TDONE ],
                      self.__tokenize(r"'a \' b'") )

  def test_escaped_spaces(self):
    self.assertEqual( [ (STRING, 'a b'), TDONE ],
                      self.__tokenize(r'a\ b') )
    self.assertEqual( [ (STRING, 'foo'), TDELIMITER, (STRING, 'a b'), TDONE ],
                      self.__tokenize(r'foo=a\ b') )
    self.assertEqual( [ (STRING, 'fo o'), TDELIMITER, (STRING, 'a b'), TDONE ],
                      self.__tokenize(r'fo\ o=a\ b') )

  def test_comment(self):
    self.assertEqual( [ (STRING, 'a'), TDELIMITER, (STRING, '1'), TSPACE, (COMMENT, '# hi'), TDONE ],
                      self.__tokenize(r'a=1 # hi') )
    self.assertEqual( [ (STRING, 'a'), TDELIMITER, (STRING, '1'), (COMMENT, '# hi'), TDONE ],
                      self.__tokenize(r'a=1# hi') )
    self.assertEqual( [ (COMMENT, '# hi'), TDONE ],
                      self.__tokenize(r'# hi') )
    self.assertEqual( [ TSPACE, (COMMENT, '# hi'), TDONE ],
                      self.__tokenize(r' # hi') )
    self.assertEqual( [ (STRING, 'a'), TDELIMITER, TSPACE, (COMMENT, '# hi'), TDONE ],
                      self.__tokenize(r'a= # hi') )
    self.assertEqual( [ (STRING, 'a'), TDELIMITER, (COMMENT, '# hi'), TDONE ],
                      self.__tokenize(r'a=# hi') )
  def test_quoted_string_inside_string(self):
    self.assertEqual( [ (STRING, 'af o o'), TDONE ],
                      self.__tokenize(r'a"f o o"') )

  def test_escaped_quote_string_inside_string(self):
    self.assertEqual( [ (STRING, 'a'), TDELIMITER, (STRING, r"'foo'"), TDONE ],
                      self.__tokenize(r'a=\'foo\'') )
    self.assertEqual( [ (STRING, 'a'), TDELIMITER, TSPACE, (STRING, r"'foo'"), TDONE ],
                      self.__tokenize(r'a= \'foo\'') )

  def test_escaped_equal_inside_string(self):
    self.assertEqual( [ (STRING, 'a='), TDELIMITER, (STRING, 'b'), TDONE ],
                      self.__tokenize(r'a\==b') )
    self.assertEqual( [ (STRING, '=a'), TDELIMITER, (STRING, 'b'), TDONE ],
                      self.__tokenize(r'\=a=b') )
    self.assertEqual( [ (STRING, 'a'), TDELIMITER, (STRING, 'b='), TDONE ],
                      self.__tokenize(r'a=b\=') )

  def test_escaped_space_inside_string(self):
    self.assertEqual( [ (STRING, 'a '), TDELIMITER, (STRING, 'b'), TDONE ],
                      self.__tokenize(r'a\ =b') )
    self.assertEqual( [ (STRING, ' a'), TDELIMITER, (STRING, 'b'), TDONE ],
                      self.__tokenize(r'\ a=b') )
    self.assertEqual( [ (STRING, 'a'), TDELIMITER, (STRING, 'b '), TDONE ],
                      self.__tokenize(r'a=b\ ') )

  def test_delimiter_is_none(self):
    self.assertEqual( [ (STRING, 'a =b'), TDONE ],
                      self.__tokenize(r'a\ =b', delimiter = None) )
    self.assertEqual( [ (STRING, 'a=b'), TDONE ],
                      self.__tokenize(r'a=b', delimiter = None) )
    self.assertEqual( [ (STRING, 'a'), TSPACE, (STRING, '=b'), TDONE ],
                      self.__tokenize(r'a =b', delimiter = None) )
    self.assertEqual( [ (STRING, 'a'), TSPACE, (STRING, '='), TSPACE, (STRING, 'b'), TDONE ],
                      self.__tokenize(r'a = b', delimiter = None) )

  def test_new_line(self):
    self.assertEqual( [ (STRING, 'a'), TDELIMITER, (STRING, 'foo'), (SPACE, ' \n '), (STRING, 'b'), TDELIMITER, (STRING, 'bar'), TDONE ],
                      self.__tokenize('a=foo \n b=bar') )

  def test_escaped_new_line(self):
    self.assertEqual( [ (STRING, 'a'), TDELIMITER, (STRING, 'f\no'), TDONE ],
                      self.__tokenize('a=f\\\no') )

  def test_keep_quotes(self):
    self.assertEqual( [ (STRING, 'a'), TDELIMITER, (STRING, 'foo bar baz'), TDONE ],
                      self.__tokenize(r'a="foo bar baz"') )
    self.assertEqual( [ (STRING, 'a'), TDELIMITER, (STRING, '"foo bar baz"'), TDONE ],
                      self.__tokenize(r'a="foo bar baz"', keep_quotes = True) )

  def test_keep_quotes_escaped(self):
    self.assertEqual( [ (STRING, 'a'), TDELIMITER, (STRING, 'foo bar baz'), TDONE ],
                      self.__tokenize(r'a="foo bar baz"') )
    self.assertEqual( [ (STRING, 'a'), TDELIMITER, (STRING, '\\"foo bar baz\\"'), TDONE ],
                      self.__tokenize(r'a="foo bar baz"', keep_quotes = True, escape_quotes = True) )

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
    print "1 keep_quotes: ", keep_quotes
    print "1 options: ", options
    return [ token for token in L.tokenize(text, delimiter, options = options) ]

  def assertEqual(self, expected, actual):
    assert isinstance(expected, list)
    expected = [ L.token(*t) for t in expected ]
    super(test_key_value_lexer, self).assertEqual(expected, actual)

if __name__ == "__main__":
  unittest.main()

#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.text.sentence_lexer import sentence_lexer as L
from bes.text.lexer_token import lexer_token
from bes.text.string_lexer_options import string_lexer_options
from helpers.token_test_helper import *

def TPUNCT(s, x = 1, y = 1): return lexer_token(L.TOKEN_PUNCTUATION, s, (x, y))

class test_sentence_lexer(unit_test):

  def test_empty_string(self):
    self.assertEqual( [ TDONE() ],
                      self._tokenize(r'') )

  def test_single_char(self):
    self.assertEqual( [ TSTRING('a'), TDONE() ],
                      self._tokenize(r'a') )
    
  def test_one_escape(self):
    self.assertEqual( [ TSTRING('a'), TDONE() ],
                      self._tokenize(r'\a') )
    
  def test_escape_backslash(self):
    self.assertEqual( [ TSTRING(r'\a'), TDONE() ],
                      self._tokenize(r'\\a') )

  def test_eos_when_escaping(self):
    self.assertEqual( [ TSTRING('a'), TDONE() ],
                      self._tokenize('a\\') )
    
  def test_simple(self):
    self.maxDiff = None
    self.assertEqual( [ TSPACE(), TSTRING('foo'), TSPACE(), TDONE() ],
                      self._tokenize(r' foo ') )
    
    self.assertEqual( [ TSPACE(), TSTRING('foo'), TSPACE(), TPUNCT('='), TSPACE(), TSTRING('123'), TSPACE('  '), TDONE() ],
                      self._tokenize(r' foo = 123  ') )

    self.assertEqual( [ TSPACE(), TSTRING('foo'), TPUNCT('='), TSPACE(), TSTRING('123'), TSPACE('  '), TDONE() ],
                      self._tokenize(r' foo= 123  ') )

    self.assertEqual( [ TSPACE(), TSTRING('foo'), TPUNCT('='), TSTRING('123'), TSPACE('  '), TDONE() ],
                      self._tokenize(r' foo=123  ') )

    self.assertEqual( [ TSPACE(), TSTRING('foo'), TPUNCT('='), TSTRING('123'), TDONE() ],
                      self._tokenize(r' foo=123') )

    self.assertEqual( [ TSTRING('foo'), TPUNCT('='), TSTRING('123'), TDONE() ],
                      self._tokenize(r'foo=123') )
    self.assertEqual( [ TSTRING('a'), TSPACE(), TSTRING('b'), TDONE() ],
                      self._tokenize(r'a b') )

  def test_quote(self):
    self.assertEqual( [ TSTRING('a b'), TDONE() ],
                      self._tokenize(r'"a b"') )
    self.assertEqual( [ TSPACE(), TSTRING('foo bar'), TSPACE(), TSTRING('a b c'), TSPACE(), TDONE() ],
                      self._tokenize(r' "foo bar" "a b c" ') )
    self.assertEqual( [ TSPACE(), TSTRING('foo bar'), TSTRING('a b c'), TSPACE(), TDONE() ],
                      self._tokenize(r' "foo bar""a b c" ') )
    self.assertEqual( [ TSTRING('foo bar'), TSTRING('a b c'), TSPACE(), TDONE() ],
                      self._tokenize(r'"foo bar""a b c" ') )
    self.assertEqual( [ TSTRING('foo bar'), TSTRING('a b c'), TDONE() ],
                      self._tokenize(r'"foo bar""a b c"') )
    
  def test_single_quote_escaped_within_quotes(self):
    self.assertEqual( [ TSTRING('a " b'), TDONE() ],
                      self._tokenize(r'"a \" b"') )
    self.assertEqual( [ TSTRING('a \' b'), TDONE() ],
                      self._tokenize(r'"a \' b"') )
    self.assertEqual( [ TSTRING('a " b'), TDONE() ],
                      self._tokenize(r"'a \" b'") )
    self.assertEqual( [ TSTRING('a \' b'), TDONE() ],
                      self._tokenize(r"'a \' b'") )

  def test_escaped_spaces(self):
    self.assertEqual( [ TSTRING('a b'), TDONE() ],
                      self._tokenize(r'a\ b') )
    self.assertEqual( [ TSTRING('foo'), TPUNCT('='), TSTRING('a b'), TDONE() ],
                      self._tokenize(r'foo=a\ b') )
    self.assertEqual( [ TSTRING('fo o'), TPUNCT('='), TSTRING('a b'), TDONE() ],
                      self._tokenize(r'fo\ o=a\ b') )

  def test_comment(self):
    self.assertEqual( [ TSTRING('a'), TPUNCT('='), TSTRING('1'), TSPACE(), TCOMMENT('# hi'), TDONE() ],
                      self._tokenize(r'a=1 # hi') )
    self.assertEqual( [ TSTRING('a'), TPUNCT('='), TSTRING('1'), TCOMMENT('# hi'), TDONE() ],
                      self._tokenize(r'a=1# hi') )
    self.assertEqual( [ TCOMMENT('# hi'), TDONE() ],
                      self._tokenize(r'# hi') )
    self.assertEqual( [ TSPACE(), TCOMMENT('# hi'), TDONE() ],
                      self._tokenize(r' # hi') )
    self.assertEqual( [ TSTRING('a'), TPUNCT('='), TSPACE(), TCOMMENT('# hi'), TDONE() ],
                      self._tokenize(r'a= # hi') )
    self.assertEqual( [ TSTRING('a'), TPUNCT('='), TCOMMENT('# hi'), TDONE() ],
                      self._tokenize(r'a=# hi') )
  def test_quoted_string_inside_string(self):
    self.assertEqual( [ TSTRING('af o o'), TDONE() ],
                      self._tokenize(r'a"f o o"') )

  def test_escaped_quote_string_inside_string(self):
    self.assertEqual( [ TSTRING('a'), TPUNCT('='), TSTRING(r"'foo'"), TDONE() ],
                      self._tokenize(r'a=\'foo\'') )
    self.assertEqual( [ TSTRING('a'), TPUNCT('='), TSPACE(), TSTRING(r"'foo'"), TDONE() ],
                      self._tokenize(r'a= \'foo\'') )

  def test_escaped_equal_inside_string(self):
    self.assertEqual( [ TSTRING('a='), TPUNCT('='), TSTRING('b'), TDONE() ],
                      self._tokenize(r'a\==b') )
    self.assertEqual( [ TSTRING('=a'), TPUNCT('='), TSTRING('b'), TDONE() ],
                      self._tokenize(r'\=a=b') )
    self.assertEqual( [ TSTRING('a'), TPUNCT('='), TSTRING('b='), TDONE() ],
                      self._tokenize(r'a=b\=') )

  def test_escaped_space_inside_string(self):
    self.assertEqual( [ TSTRING('a '), TPUNCT('='), TSTRING('b'), TDONE() ],
                      self._tokenize(r'a\ =b') )
    self.assertEqual( [ TSTRING(' a'), TPUNCT('='), TSTRING('b'), TDONE() ],
                      self._tokenize(r'\ a=b') )
    self.assertEqual( [ TSTRING('a'), TPUNCT('='), TSTRING('b '), TDONE() ],
                      self._tokenize(r'a=b\ ') )

  def test_new_line(self):
    self.assertEqual( [ TSTRING('a'), TPUNCT('='), TSTRING('foo'), TSPACE(' \n ', y = 2), TSTRING('b', y = 2), TPUNCT('=', y = 2), TSTRING('bar', y = 2), TDONE(y = 2) ],
                      self._tokenize('a=foo \n b=bar') )

  def test_escaped_new_line(self):
    self.assertEqual( [ TSTRING('a'), TPUNCT('='), TSTRING('f\no', y = 2), TDONE(y = 2) ],
                      self._tokenize('a=f\\\no') )

  def test_keep_quotes(self):
    self.assertEqual( [ TSTRING('a'), TPUNCT('='), TSTRING('foo bar baz'), TDONE() ],
                      self._tokenize(r'a="foo bar baz"') )
    self.assertEqual( [ TSTRING('a'), TPUNCT('='), TSTRING('"foo bar baz"'), TDONE() ],
                      self._tokenize(r'a="foo bar baz"', keep_quotes = True) )

  def test_keep_quotes_escaped(self):
    self.assertEqual( [ TSTRING('a'), TPUNCT('='), TSTRING('foo bar baz'), TDONE() ],
                      self._tokenize(r'a="foo bar baz"') )
    self.assertEqual( [ TSTRING('a'), TPUNCT('='), TSTRING('\\"foo bar baz\\"'), TDONE() ],
                      self._tokenize(r'a="foo bar baz"', keep_quotes = True, escape_quotes = True) )

  def test_line_numbers(self):
    '''
    1: a=5
    2: b=6
    3: 
    4: c=7
    5:
    '''
    self.assertEqual( [ TSTRING('a'), TPUNCT('='), TSTRING('5'), TSPACE('\n', y = 2), 
                        TSTRING('b', y = 2), TPUNCT('=', y = 2), TSTRING('6', y = 2), TSPACE('\n\n', y = 4),
#                        TSPACE('\n\n', y = 4), 
                        TSTRING('c', y = 4), TPUNCT('=', y = 4), TSTRING('7', y = 4), TSPACE('\n', y = 5), 
                        TDONE(y = 5) ],
                      self._tokenize('a=5\nb=6\n\nc=7\n') )

  def test_punctuation(self):
    self.assertEqual( [ TSTRING('a'), TPUNCT('&'), TSTRING('b'), TDONE() ],
                      self._tokenize('a&b') )

    self.assertEqual( [ TSTRING('a'), TPUNCT('&'), TPUNCT('&'), TSTRING('b'), TDONE() ],
                      self._tokenize('a&&b') )

  def test_underscore(self):
    self.assertEqual( [ TSPACE(), TSTRING('foo_bar'), TSPACE(), TDONE() ],
                      self._tokenize(r' foo_bar ') )
    
  def test_ignore_comments(self):
    self.assertEqual( [ TSTRING('foo'), TSPACE(), TSTRING('#bar'), TDONE() ],
                      self._tokenize(r'foo #bar', ignore_comments = True) )
    
  @classmethod
  def _tokenize(self, text,
                keep_quotes = False,
                escape_quotes = False,
                ignore_comments = False,
                ignore_spaces = False):
    options = 0
    if keep_quotes:
      options |= string_lexer_options.KEEP_QUOTES
    if escape_quotes:
      options |= string_lexer_options.ESCAPE_QUOTES
    if ignore_comments:
      options |= string_lexer_options.IGNORE_COMMENTS
    if ignore_spaces:
      options |= string_lexer_options.IGNORE_SPACES
    return [ token for token in L.tokenize(text, options = options) ]

  def assertEqual(self, expected, actual):
    assert isinstance(expected, list)
    expected = [ lexer_token(*t) for t in expected ]
    super(test_sentence_lexer, self).assertEqual(expected, actual)

if __name__ == '__main__':
  unit_test.main()

#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.config.ini.bc_ini_lexer_token import bc_ini_lexer_token
from bes.config.ini.bc_ini_lexer import bc_ini_lexer as L
from bes.config.ini.bc_ini_lexer_options import bc_ini_lexer_options
from helpers.token_test_helper import *

class test_bc_ini_lexer(unit_test):

  def test_empty_string(self):
    self.assertEqual( [],
                      self._tokenize(r'') )

  def test_single_char(self):
    self.assertEqual( [ TSTRING('a') ],
                      self._tokenize(r'a') )
    
  def test_one_escape(self):
    self.assertEqual( [ TSTRING('a') ],
                      self._tokenize(r'\a') )
    
  def test_escape_backslash(self):
    self.assertEqual( [ TSTRING(r'\a') ],
                      self._tokenize(r'\\a') )

  def test_eos_when_escaping(self):
    self.assertEqual( [ TSTRING('a') ],
                      self._tokenize('a\\') )
    
  def test_simple(self):
    self.maxDiff = None
    self.assertEqual( [ TSPACE(), TSTRING('foo'), TSPACE() ],
                      self._tokenize(r' foo ') )
    
    self.assertEqual( [ TSPACE(), TSTRING('foo'), TSPACE(), TSTRING('='), TSPACE(), TSTRING('123'), TSPACE('  ') ],
                      self._tokenize(r' foo = 123  ') )

    self.assertEqual( [ TSPACE(), TSTRING('foo='), TSPACE(), TSTRING('123'), TSPACE('  ') ],
                      self._tokenize(r' foo= 123  ') )

    self.assertEqual( [ TSPACE(), TSTRING('foo=123'), TSPACE('  ') ],
                      self._tokenize(r' foo=123  ') )

    self.assertEqual( [ TSPACE(), TSTRING('foo=123') ],
                      self._tokenize(r' foo=123') )

    self.assertEqual( [ TSTRING('foo=123') ],
                      self._tokenize(r'foo=123') )
    self.assertEqual( [ TSTRING('a'), TSPACE(), TSTRING('b') ],
                      self._tokenize(r'a b') )

  def test_quote(self):
    self.assertEqual( [ TSTRING('a b') ],
                      self._tokenize(r'"a b"') )
    self.assertEqual( [ TSPACE(), TSTRING('foo bar'), TSPACE(), TSTRING('a b c'), TSPACE() ],
                      self._tokenize(r' "foo bar" "a b c" ') )
    self.assertEqual( [ TSPACE(), TSTRING('foo bar'), TSTRING('a b c'), TSPACE() ],
                      self._tokenize(r' "foo bar""a b c" ') )
    self.assertEqual( [ TSTRING('foo bar'), TSTRING('a b c'), TSPACE() ],
                      self._tokenize(r'"foo bar""a b c" ') )
    self.assertEqual( [ TSTRING('foo bar'), TSTRING('a b c') ],
                      self._tokenize(r'"foo bar""a b c"') )
    
  def test_single_quote_escaped_within_quotes(self):
    self.assertEqual( [ TSTRING('a " b') ],
                      self._tokenize(r'"a \" b"') )
    self.assertEqual( [ TSTRING('a \' b') ],
                      self._tokenize(r'"a \' b"') )
    self.assertEqual( [ TSTRING('a " b') ],
                      self._tokenize(r"'a \" b'") )
    self.assertEqual( [ TSTRING('a \' b') ],
                      self._tokenize(r"'a \' b'") )

  def test_escaped_spaces(self):
    self.assertEqual( [ TSTRING('a b') ],
                      self._tokenize(r'a\ b') )
    self.assertEqual( [ TSTRING('foo=a b') ],
                      self._tokenize(r'foo=a\ b') )
    self.assertEqual( [ TSTRING('fo o=a b') ],
                      self._tokenize(r'fo\ o=a\ b') )

  def test_comment(self):
    self.assertEqual( [ TSTRING('a=1'), TSPACE(), TCOMMENT('; hi') ],
                      self._tokenize(r'a=1 ; hi') )
    self.assertEqual( [ TSTRING('a=1'), TCOMMENT('; hi') ],
                      self._tokenize(r'a=1; hi') )
    self.assertEqual( [ TCOMMENT('; hi') ],
                      self._tokenize(r'; hi') )
    self.assertEqual( [ TSPACE(), TCOMMENT('; hi') ],
                      self._tokenize(r' ; hi') )
    self.assertEqual( [ TSTRING('a='), TSPACE(), TCOMMENT('; hi') ],
                      self._tokenize(r'a= ; hi') )
    self.assertEqual( [ TSTRING('a='), TCOMMENT('; hi') ],
                      self._tokenize(r'a=; hi') )
  def test_quoted_string_inside_string(self):
    self.assertEqual( [ TSTRING('af o o') ],
                      self._tokenize(r'a"f o o"') )

  def test_escaped_quote_string_inside_string(self):
    self.assertEqual( [ TSTRING(r"a='foo'") ],
                      self._tokenize(r'a=\'foo\'') )
    self.assertEqual( [ TSTRING('a='), TSPACE(), TSTRING(r"'foo'") ],
                      self._tokenize(r'a= \'foo\'') )

  def test_escaped_equal_inside_string(self):
    self.assertEqual( [ TSTRING('a==b') ],
                      self._tokenize(r'a\==b') )
    self.assertEqual( [ TSTRING('=a=b') ],
                      self._tokenize(r'\=a=b') )
    self.assertEqual( [ TSTRING('a=b=') ],
                      self._tokenize(r'a=b\=') )

  def test_escaped_space_inside_string(self):
    self.assertEqual( [ TSTRING('a =b') ],
                      self._tokenize(r'a\ =b') )
    self.assertEqual( [ TSTRING(' a=b') ],
                      self._tokenize(r'\ a=b') )
    self.assertEqual( [ TSTRING('a=b ') ],
                      self._tokenize(r'a=b\ ') )

  def xtest_delimiter_is_none(self):
    self.assertEqual( [ TSTRING('a =b') ],
                      self._tokenize(r'a\ =b', delimiter = None) )
    self.assertEqual( [ TSTRING('a=b') ],
                      self._tokenize(r'a=b', delimiter = None) )
    self.assertEqual( [ TSTRING('a'), TSPACE(), TSTRING('=b') ],
                      self._tokenize(r'a =b', delimiter = None) )
    self.assertEqual( [ TSTRING('a'), TSPACE(), TSTRING('='), TSPACE(), TSTRING('b') ],
                      self._tokenize(r'a = b', delimiter = None) )

  def test_new_line(self):
    self.assertEqual( [ TSTRING('a=foo'), TSPACE(' \n ', y = 2), TSTRING('b=bar', y = 2) ],
                      self._tokenize('a=foo \n b=bar') )

  def test_escaped_new_line(self):
    self.assertEqual( [ TSTRING('a=f\no', y = 2) ],
                      self._tokenize('a=f\\\no') )

  def test_keep_quotes(self):
    self.assertEqual( [ TSTRING('a=foo bar baz') ],
                      self._tokenize(r'a="foo bar baz"') )
    self.assertEqual( [ TSTRING('a="foo bar baz"') ],
                      self._tokenize(r'a="foo bar baz"', keep_quotes = True) )

  def test_keep_quotes_escaped(self):
    self.assertEqual( [ TSTRING('a=foo bar baz') ],
                      self._tokenize(r'a="foo bar baz"') )
    self.assertEqual( [ TSTRING('a=\\"foo bar baz\\"') ],
                      self._tokenize(r'a="foo bar baz"', keep_quotes = True, escape_quotes = True) )

  def test_line_numbers(self):
    '''
    1: a=5
    2: b=6
    3: 
    4: c=7
    5:
    '''
    self.assertEqual( [ TSTRING('a=5'), TSPACE('\n', y = 2), 
                        TSTRING('b=6', y = 2), TSPACE('\n\n', y = 4),
                        TSTRING('c=7', y = 4), TSPACE('\n', y = 5)
                       ],
                      self._tokenize('a=5\nb=6\n\nc=7\n') )

  def test_ignore_comments(self):
    self.assertEqual( [ TSTRING('foo'), TSPACE(), TSTRING(';bar') ],
                      self._tokenize('foo ;bar', ignore_comments = True) )
    
  @classmethod
  def _tokenize(self, text, delimiter = '=',
                 keep_quotes = False,
                 escape_quotes = False,
                 ignore_comments = False):
    options = 0
    if keep_quotes:
      options |= bc_ini_lexer_options.KEEP_QUOTES
    if escape_quotes:
      options |= bc_ini_lexer_options.ESCAPE_QUOTES
    if ignore_comments:
      options |= bc_ini_lexer_options.IGNORE_COMMENTS
    return [ token for token in L.tokenize(text, delimiter, options = options) ]

  def assertEqual(self, expected, actual):
    assert isinstance(expected, list)
    expected = [ bc_ini_lexer_token(*t) for t in expected ]
    super().assertEqual(expected, actual)

if __name__ == '__main__':
  unit_test.main()

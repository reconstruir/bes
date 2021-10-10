#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import unittest
from bes.text.string_list_parser import string_list_parser as P
from bes.text.string_lexer_options import string_lexer_options

class test_string_list_parser(unittest.TestCase):

  def test_empty(self):
    self.assertEqual( [], self._parse('') )
    
  def test_parse_simple(self):
    self.assertEqual( [ 'foo', 'bar' ], self._parse('foo bar') ) 

  def test_parse_single_quoted(self):
    self.assertEqual( [ 'f o o', 'b a r' ], self._parse('"f o o" "b a r"') )
    self.assertEqual( [ 'f o o', 'b a r' ], self._parse(r'f\ o\ o b\ a\ r') )

  def test_parse_quote_values(self):
    self.assertEqual( [ '-DNAME="f o o"', '"b a r"' ], self._parse('-DNAME="f o o" "b a r"', keep_quotes = True) )
    self.assertEqual( [ '-DNAME=f o o', 'b a r' ], self._parse(r'-DNAME=f\ o\ o b\ a\ r', keep_quotes = True) )
    self.assertEqual( [ '-DNAME="foo bar"' ], self._parse('-DNAME="foo bar"', keep_quotes = True) )
    self.assertEqual( [ '-DNAME=\\"foo bar\\"' ], self._parse('-DNAME="foo bar"', keep_quotes = True, escape_quotes = True) )

  def test_comment_in_quote(self):
    self.assertEqual( [ '"foo #bar"', '"kiwi #apple"' ], self._parse('"foo #bar" "kiwi #apple"', keep_quotes = True) )
    
  def test_comment(self):
    self.assertEqual( [], self._parse('#comment') )
    
  def test_ignore_comments(self):
    self.assertEqual( ['#foo', '#bar' ], self._parse('#foo  #bar', ignore_comments = True) )
    
  @classmethod
  def _parse(self, text,
             keep_quotes = False,
             escape_quotes = False,
             ignore_comments = False):
    options = 0
    if keep_quotes:
      options |= string_lexer_options.KEEP_QUOTES
    if escape_quotes:
      options |= string_lexer_options.ESCAPE_QUOTES
    if ignore_comments:
      options |= string_lexer_options.IGNORE_COMMENTS
    return P.parse_to_list(text, options = options)

if __name__ == "__main__":
  unittest.main()

#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import unittest
from bes.text import string_list_parser as P

class test_string_list_parser(unittest.TestCase):

  def test_empty(self):
    self.assertEqual( [], self.__parse('') )
    
  def test_parse_simple(self):
    self.assertEqual( [ 'foo', 'bar' ], self.__parse('foo bar') ) 

  def test_parse_single_quoted(self):
    self.assertEqual( [ 'f o o', 'b a r' ], self.__parse('"f o o" "b a r"') )
    self.assertEqual( [ 'f o o', 'b a r' ], self.__parse('f\ o\ o b\ a\ r') )

  def test_parse_quote_values(self):
    self.assertEqual( [ '-DNAME="f o o"', '"b a r"' ], self.__parse('-DNAME="f o o" "b a r"', keep_quotes = True) )
    self.assertEqual( [ '-DNAME=f o o', 'b a r' ], self.__parse('-DNAME=f\ o\ o b\ a\ r', keep_quotes = True) )
    self.assertEqual( [ '-DNAME="foo bar"' ], self.__parse('-DNAME="foo bar"', keep_quotes = True) )
    self.assertEqual( [ '-DNAME=\\"foo bar\\"' ], self.__parse('-DNAME="foo bar"', keep_quotes = True, escape_quotes = True) )

  def test_comment_in_quote(self):
    self.assertEqual( [ '"foo #bar"', '"kiwi #apple"' ], self.__parse('"foo #bar" "kiwi #apple"', keep_quotes = True) )
    
  @classmethod
  def __parse(self, text,
              keep_quotes = False,
              escape_quotes = False,
              ignore_comments = False):
    options = 0
    if keep_quotes:
      options |= P.KEEP_QUOTES
    if escape_quotes:
      options |= P.ESCAPE_QUOTES
    if ignore_comments:
      options |= P.IGNORE_COMMENTS
    return P.parse_to_list(text, options = options)

if __name__ == "__main__":
  unittest.main()

#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import unittest
from bes.key_value.key_value_parser import key_value_parser as P
from bes.key_value.key_value import key_value as KV

class test_key_value_parser(unittest.TestCase):

  def test_empty(self):
    self.assertEqual( [ ], self._parse('') )
    
  def test_parse_key_values(self):
    self.assertEqual( [ KV('foo', '123'), KV('bar', 'hello') ], self._parse('foo=123  bar=hello') )
    self.assertEqual( [ KV('foo', '1 2 3'), KV('bar', 'hello') ], self._parse('foo=\"1 2 3\" bar=hello') )
    self.assertEqual( [ KV('foo', '1 2 3'), KV('bar', 'hello') ], self._parse(' foo=\"1 2 3\" bar=hello ') )
    self.assertEqual( [ KV('foo', '1 2 3'), KV('bar', 'hello') ], self._parse(' foo=\"1 2 3\" bar=hello ') )
    self.assertEqual( [ KV('f oo', '1 2 3'), KV('bar', 'hello') ], self._parse(' f\ oo=\"1 2 3\" bar=hello ') )
    self.assertEqual( [ KV('foo', '1 2 3'), KV('bar', 'hello') ], self._parse(' foo=1\ 2\ 3 bar=hello ') )

  def test_empty_value(self):
    self.maxDiff = None
    self.assertEqual( [ KV('foo', None) ], self._parse('foo=') )
    self.assertEqual( [ KV('foo', None) ], self._parse('foo= ') )
    self.assertEqual( [ KV('foo', None) ], self._parse(' foo= ') )
    self.assertEqual( [ KV('foo', None), KV('bar', None) ], self._parse('foo= bar=') )
    self.assertEqual( [ KV('foo', None), KV('bar', None) ], self._parse('foo=    bar=') )

  def test_empty_value_not_default(self):
    self.maxDiff = None
    self.assertEqual( [ KV('foo', 'X') ], self._parse('foo=', empty_value = 'X') )
    self.assertEqual( [ KV('foo', 'X') ], self._parse('foo= ', empty_value = 'X') )
    self.assertEqual( [ KV('foo', 'X') ], self._parse(' foo= ', empty_value = 'X') )
    self.assertEqual( [ KV('foo', 'X'), KV('bar', 'X') ], self._parse('foo= bar=', empty_value = 'X') )
    self.assertEqual( [ KV('foo', 'X'), KV('bar', 'X') ], self._parse('foo=    bar=', empty_value = 'X') )

  def test_more(self):
    self.assertEqual( { 'foo': '123', 'bar': 'hello' }, P.parse_to_dict('foo=123\t\nbar=hello') )
    self.assertEqual( { 'foo': None }, P.parse_to_dict('foo=') )
    self.assertEqual( { 'foo': None }, P.parse_to_dict('foo= ') )
    self.assertEqual( { 'foo': None }, P.parse_to_dict(' foo=') )
    self.assertEqual( { 'foo': None }, P.parse_to_dict(' foo= ') )
    self.assertEqual( { 'foo': '5' }, P.parse_to_dict('foo=5') )
    self.assertEqual( { 'foo': '5' }, P.parse_to_dict('foo=5 ') )
    self.assertEqual( { 'foo': '5' }, P.parse_to_dict(' foo=5') )
    self.assertEqual( { 'foo': '5' }, P.parse_to_dict(' foo=5 ') )
    self.assertEqual( { 'foo': '5', 'bar': None }, P.parse_to_dict('foo=5 bar=') )

  def test_parse_key_values_single_quoted(self):
    self.assertEqual( { 'foo': 'x' }, P.parse_to_dict('foo="x"') )
    self.assertEqual( { 'foo': '5', 'bar': 'hi' }, P.parse_to_dict('foo=5 bar="hi"') )
    self.assertEqual( { 'foo': '5', 'bar': '' }, P.parse_to_dict('foo=5 bar=""') )
    self.assertEqual( { 'foo': '5', 'bar': 'a b c' }, P.parse_to_dict('foo=5 bar="a b c"') )
    self.assertEqual( { 'foo': '5', 'bar': 'a b c', 'baz': None }, P.parse_to_dict('foo=5 bar="a b c" baz=') )

  def test_parse_key_values_double_quoted(self):
    self.assertEqual( { 'foo': 'x' }, P.parse_to_dict('foo=\'x\'') )
    self.assertEqual( { 'foo': '5', 'bar': 'hi' }, P.parse_to_dict('foo=5 bar=\'hi\'') )
    self.assertEqual( { 'foo': '5', 'bar': '' }, P.parse_to_dict('foo=5 bar=\'\'') )
    self.assertEqual( { 'foo': '5', 'bar': 'a b c' }, P.parse_to_dict('foo=5 bar=\'a b c\'') )

  def test_parse_key_values_quoted_inside_quotes(self):
    self.assertEqual( { 'foo': 'This is "good"' }, P.parse_to_dict('foo=\'This is "good"\'') )

  def test_comment(self):
    self.assertEqual( { 'foo': '555' }, P.parse_to_dict('foo=555 # comment') )
    self.assertEqual( { 'foo': '555' }, P.parse_to_dict('foo=555# comment') )
    self.assertEqual( { 'foo': '555' }, P.parse_to_dict('foo=555#') )
    self.assertEqual( { 'foo': None }, P.parse_to_dict('foo=#') )
    self.assertEqual( { 'foo': None }, P.parse_to_dict('foo#') )
    self.assertEqual( { }, P.parse_to_dict('#') )

  def test_parse_keep_quotes(self):
    self.assertEqual( { 'foo': 'a b c' }, P.parse_to_dict('foo="a b c"', options = 0) )
    self.assertEqual( { 'foo': '"a b c"' }, P.parse_to_dict('foo="a b c"', options = P.KEEP_QUOTES) )
    self.assertEqual( { 'foo': '""a b c""' }, P.parse_to_dict(r'foo=\""a b c\""', options = P.KEEP_QUOTES) )
    self.assertEqual( { 'foo': 'abc' }, P.parse_to_dict('foo=abc', options = P.KEEP_QUOTES) )
    self.assertEqual( { 'foo': None }, P.parse_to_dict('foo=', options = P.KEEP_QUOTES) )
    self.assertEqual( { 'foo': 'bar:"a b"' }, P.parse_to_dict(r'foo=bar\:"a b"', options = P.KEEP_QUOTES) )
    self.assertEqual( { 'foo': 'bar:\\"a b\\"' }, P.parse_to_dict(r'foo=bar\:"a b"', options = P.KEEP_QUOTES | P.ESCAPE_QUOTES) )

  def test_comment_in_quote(self):
    self.assertEqual( { 'foo': 'a #b c' }, P.parse_to_dict('foo="a #b c"') )
    self.assertEqual( { 'foo': 'a #b c' }, P.parse_to_dict('foo=\'a #b c\'') )
    
  def test_ignore_comments(self):
    self.assertEqual( [ KV('foo', '#bar'), KV('fruit', '#orange') ] , self._parse('foo=#bar fruit=#orange', ignore_comments = True) )

  def test_escaped_equal(self):
    self.assertEqual( [ KV('foo', 'bar=baz') ] , self._parse('foo=bar\=baz') )

  @classmethod
  def _parse(self, text,
             keep_quotes = False,
             escape_quotes = False,
             ignore_comments = False,
             empty_value = None):
    options = 0
    if keep_quotes:
      options |= P.KEEP_QUOTES
    if escape_quotes:
      options |= P.ESCAPE_QUOTES
    if ignore_comments:
      options |= P.IGNORE_COMMENTS
    return P.parse_to_list(text, options = options, empty_value = empty_value, log_tag = 'test_key_value_parser')

if __name__ == "__main__":
  unittest.main()

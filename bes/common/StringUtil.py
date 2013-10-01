#!/usr/bin/env python
#-*- coding:utf-8 -*-

import re, StringIO
import unittest

class StringUtil(object):
  'String util'

  @classmethod
  def replace_white_space(clazz, s, replacement):
    'Replace white space sequences in s with replacement.'
    buf = StringIO.StringIO()
    STATE_CHAR = 1
    STATE_SPACE = 2

    state = STATE_CHAR
    for c in s:
      if state == STATE_CHAR:
        if c.isspace():
          buf.write(replacement)
          state = STATE_SPACE
        else:
          buf.write(c)
      elif state == STATE_SPACE:
        if not c.isspace():
          buf.write(c)
          state = STATE_CHAR
    return buf.getvalue()

  @classmethod
  def split_by_white_space(clazz, s):
    'Split the string into tokens by white space.'
    tokens = re.split('\s+', s)
    return [ token for token in tokens if token ]

  @classmethod
  def remove_head(clazz, s, head):
    if isinstance(head, str):
      if s.startswith(head):
        return s[len(head):]
      return s
    elif isinstance(head, list):
      for h in head:
        s = clazz.remove_head(s, h)
      return s

  @classmethod
  def remove_tail(clazz, s, tail):
    if isinstance(tail, str):
      if s.endswith(tail):
        return s[0:-len(tail)]
      return s
    elif isinstance(tail, list):
      for t in tail:
        s = clazz.remove_tail(s, t)
      return s

  @classmethod
  def replace(clazz, s, d):
    'Replace all instances of dict d in string s.'
    for key, value in d.items():
      s = s.replace(key, value)
    return s

  @classmethod
  def is_string(clazz, s):
    'Return True if s is a string.'
    return isinstance(s, (str, unicode))

  @classmethod
  def flatten(clazz, s, delimiter = ' '):
    'Flatten the given collection to a string.'
    'If s is already a string just return it.'
    if clazz.is_string(s):
      return s
    if isinstance(s, list):
      return delimiter.join(s)
    raise RuntimeError('Not a string or list')

  @classmethod
  def unquote(clazz, s):
    'Unquote a string.'
    for quote in [ '\'', '\"' ]:
      if s.startswith(quote) and s.endswith(quote):
        return s[1:-1]
    return s

class TestStringUtil(unittest.TestCase):

  def test_replace_white_space(self):
    self.assertEqual( 'a b c', StringUtil.replace_white_space('a   b   c', ' ') )
    self.assertEqual( 'a b c', StringUtil.replace_white_space('a b c', ' ') )
    self.assertEqual( 'a b c', StringUtil.replace_white_space('a  b  c', ' ') )
    self.assertEqual( ' a b c', StringUtil.replace_white_space(' a  b  c', ' ') )
    self.assertEqual( ' a b c', StringUtil.replace_white_space('  a  b  c', ' ') )
    self.assertEqual( 'a b c ', StringUtil.replace_white_space('a   b   c ', ' ') )
    self.assertEqual( 'a b c ', StringUtil.replace_white_space('a   b   c  ', ' ') )
    self.assertEqual( 'a b c ', StringUtil.replace_white_space('a   b   c   ', ' ') )
    self.assertEqual( 'a_b_c_', StringUtil.replace_white_space('a   b   c   ', '_') )
    self.assertEqual( '_a_b_c_', StringUtil.replace_white_space(' a   b   c   ', '_') )

  def test_split_by_white_space(self):
    self.assertEqual( [ 'a', 'b', 'c' ], StringUtil.split_by_white_space('a b c') )
    self.assertEqual( [ 'a', 'b', 'c' ], StringUtil.split_by_white_space(' a b c') )
    self.assertEqual( [ 'a', 'b', 'c' ], StringUtil.split_by_white_space(' a b c ') )
    self.assertEqual( [ 'a', 'b', 'c' ], StringUtil.split_by_white_space(' a b  c ') )
    self.assertEqual( [], StringUtil.split_by_white_space('') )
    self.assertEqual( ['a'], StringUtil.split_by_white_space('a') )

  def test_remove_tail(self):
    self.assertEqual( 'fo', StringUtil.remove_tail('foobar', [ 'bar', 'o' ]) )

  def test_remove_head(self):
    self.assertEqual( 'ar', StringUtil.remove_head('foobar', [ 'foo', 'b' ]) )

  def test_replace(self):
    self.assertEqual( 'foo bar', StringUtil.replace('a b', { 'a': 'foo', 'b': 'bar' }) )

  def test_flatten(self):
    self.assertEqual( 'foo bar', StringUtil.flatten('foo bar') )
    self.assertEqual( 'foo bar', StringUtil.flatten(['foo', 'bar']) )

  def test_is_string(self):
    self.assertEqual( True, StringUtil.is_string('foo') )
    self.assertEqual( True, StringUtil.is_string(u'foo') )
    self.assertEqual( True, StringUtil.is_string(r'foo') )
    self.assertEqual( False, StringUtil.is_string(['foo']) )
    self.assertEqual( False, StringUtil.is_string(False) )

  def test_unquote(self):
    self.assertEqual( 'foo', StringUtil.unquote('\'foo\'') )
    self.assertEqual( 'foo', StringUtil.unquote('\"foo\"') )
    self.assertEqual( '\'foo\"', StringUtil.unquote('\'foo\"') )
    self.assertEqual( '\'foo', StringUtil.unquote('\'foo') )
    self.assertEqual( 'foo\'', StringUtil.unquote('foo\'') )

if __name__ == "__main__":
  unittest.main()

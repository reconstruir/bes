#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import re, sys

from bes.compat import StringIO
from bes.system import compat
from .check_type import check_type

class string_util(object):
  'String util'

  @classmethod
  def replace_white_space(clazz, s, replacement):
    'Replace white space sequences in s with replacement.'
    buf = StringIO()
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
  def split_by_white_space(clazz, s, strip = False):
    'Split the string into tokens by white space.'
    tokens = re.split('\s+', s)
    if strip:
      return [ token.strip() for token in tokens if token ]
    else:
      return [ token for token in tokens if token ]

  @classmethod
  def remove_head(clazz, s, head):
    if compat.is_string(head):
      if s.startswith(head):
        return s[len(head):]
      return s
    elif isinstance(head, list):
      for h in head:
        s = clazz.remove_head(s, h)
      return s

  @classmethod
  def remove_tail(clazz, s, tail):
    if compat.is_string(tail):
      if s.endswith(tail):
        return s[0:-len(tail)]
      return s
    elif isinstance(tail, list):
      for t in tail:
        s = clazz.remove_tail(s, t)
      return s

  @classmethod
  def replace(clazz, s, replacements, word_boundary = True):
    'Replace all instances of dict d in string s.'
    check_type.check_string(s, 's')
    check_type.check_dict(replacements, 'replacements')
    assert clazz.is_string(s)
    for key, value in replacements.items():
      assert key
      if word_boundary:
        pattern_parts = []
        if key[0].isalnum():
          pattern_parts.append(r'\b')
        pattern_parts.append(re.escape(key))
        if key[-1].isalnum():
          pattern_parts.append(r'\b')
        pattern = ''.join(pattern_parts)
        s = re.sub(pattern, value, s)
      else:
        s = s.replace(key, value)
    return s

  @classmethod
  def is_string(clazz, s):
    'Return True if s is a string.'
    return compat.is_string(s)
    
  @classmethod
  def is_char(clazz, s):
    'Return True if s is 1 line character.'
    return clazz.is_string(s) and len(s) == 1

  @classmethod
  def is_ascii(clazz, s):
    'Return True if s is ascii.'
    try:
      s.decode('ascii')
      return True
    except:
      return False

  @classmethod
  def flatten(clazz, s, delimiter = ' '):
    'Flatten the given collection to a string.'
    'If s is already a string just return it.'
    if clazz.is_string(s):
      return s
    if isinstance(s, list):
      return delimiter.join(s)
    raise TypeError('Not a string or list')

  JUSTIFY_LEFT = 1
  JUSTIFY_RIGHT = 2
  @classmethod
  def justify(clazz, s, justification, width, fill = ' '):
    'Justify a string within width with fill.'
    assert len(fill) == 1
    assert justification in [ clazz.JUSTIFY_LEFT, clazz.JUSTIFY_RIGHT ]
    length = len(s)
    if length >= width:
      return s
    fill_string = fill * (width - length)
    if justification == clazz.JUSTIFY_LEFT:
      return s + fill_string
    else:
      return fill_string + s

  @classmethod
  def left_justify(clazz, s, width, fill = ' '):
    'Left justify a string within width with fill.'
    return clazz.justify(s, clazz.JUSTIFY_LEFT, width, fill = fill)

  @classmethod
  def right_justify(clazz, s, width, fill = ' '):
    'Right justify a string within width with fill.'
    return clazz.justify(s, clazz.JUSTIFY_RIGHT, width, fill = fill)

  @classmethod
  def quote(clazz, s, quote_char = None):
    'Quote a string.'
    if quote_char:
      if clazz.is_quoted(s, quote_char = quote_char):
        return s
      if quote_char == '"' and clazz.is_single_quoted(s) or quote_char == "'" and clazz.is_double_quoted(s):
        s = clazz.unquote(s)
      return quote_char + s + quote_char
    if clazz.is_quoted(s):
      return s
    has_single_quote = "'" in s
    has_double_quote = '"' in s
    if has_single_quote and has_double_quote:
      raise RuntimeError('Cannot quote a string with both single and double quotes: %s' % (s))
    if has_double_quote:
      return "'" + s + "'"
    return '"' + s + '"'

  @classmethod
  def unquote(clazz, s):
    'Unquote a string.'
    if not clazz.is_quoted(s):
      return s
    return s[1:-1]
  
  @classmethod
  def is_quoted(clazz, s, quote_char = None):
    'Return True if s is quoted.'
    if len(s) < 2:
      return False
    if quote_char:
      quote_chars = [ quote_char ]
    else:
      quote_chars = [ r'"', r"'" ]
    for quote in quote_chars:
      if s[0] == s[-1] == quote:
        return True
    return False

  @classmethod
  def is_single_quoted(clazz, s):
    'Return True if s is single quoted.'
    return clazz.is_quoted(s, quote_char = "'")

  @classmethod
  def is_double_quoted(clazz, s):
    'Return True if s is doubleb quoted.'
    return clazz.is_quoted(s, quote_char = '"')

  @classmethod
  def quote_if_needed(clazz, s, quote_char = None):
    if clazz.has_white_space(s):
      return clazz.quote(s, quote_char = quote_char)
    else:
      return s

  @classmethod
  def escape_quotes(clazz, s):
    'Escape any single or double quotes in s.'
    s = s.replace(r"'", "\\'")
    s = s.replace(r'"', '\\"')
    return s

  @classmethod
  def escape_spaces(clazz, s):
    'Escape spaces in s.'
    s = s.replace(r" ", "\\ ")
    return s

  @classmethod
  def has_white_space(clazz, s):
    'Return True if s has any white space.'
    for c in s:
      if c.isspace():
        return True
    return False

  @classmethod
  def has_white_space(clazz, s):
    'Return True if s has any white space.'
    for c in s:
      if c.isspace():
        return True
    return False

  @classmethod
  def reverse(clazz, s):
    return ''.join(reversed(s))

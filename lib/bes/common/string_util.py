#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import re
import string
import sys

from bes.compat.StringIO import StringIO
from bes.system.compat import compat
from bes.system.check import check

from .char_util import char_util

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
    tokens = re.split(r'\s+', s)
    if strip:
      return [ token.strip() for token in tokens if token.strip() ]
    else:
      return [ token for token in tokens if token ]

  @classmethod
  def partition_by_white_space(clazz, s, strip = False):
    'Split the string into tokens by white space.'
    found = re.search(r'\s+', s)
    if not found:
      if strip:
        s = s.strip()
      return ( s, '', '' )
    head = s[0:found.start()]
    delimiter = s[found.start():found.end()]
    tail = s[found.end():]
    if strip:
      head = head.strip()
    if strip:
      tail = tail.strip()
    return ( head, delimiter, tail )

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
  def replace(clazz, s, replacements, word_boundary = True, underscore = False):
    'Replace all instances of dict d in string s.'
    check.check_string(s)
    check.check_dict(replacements, check.STRING_TYPES, check.STRING_TYPES)
    check.check_bool(word_boundary)
    check.check_bool(underscore)

    for src_string, dst_string in replacements.items():
      s = clazz.replace_all(s, src_string, dst_string,
                            word_boundary = word_boundary,
                            underscore = underscore)
    return s

  @classmethod
  def find_all(clazz, s, sub_string):
    'Yields all the indeces of sub_string in s'
    check.check_string(s)
    check.check_string(sub_string)

    i = 0
    while True:
      i = s.find(sub_string, i)
      if i < 0:
        return
      yield i
      i += len(sub_string)

  @classmethod
  def replace_span(clazz, s, i, n, replacement, word_boundary = False, underscore = False):
    'Replace a span of text in s starting at i with a length of n'
    check.check_string(s)
    check.check_int(i)
    check.check_int(n)
    check.check_string(replacement)
    check.check_bool(word_boundary)
    check.check_bool(underscore)

    if i < 0:
      raise ValueError('i should be greater than 0')
    length = len(s)
    if i >= len(s):
      raise ValueError(f'n should be less than the length of s - {length}')
    if n < 1:
      raise ValueError('n should be at least 1')
    
    j = i + n - 1
    assert j >= i

    #print(f's={s} i={i} n={n}')
    if word_boundary:
      if i >= 1:
        prev_char = s[i - 1]
        prev_char_is_boundary = char_util.is_word_boundary(prev_char, underscore = underscore)
        #print(f'prev_char={prev_char} prev_char_is_boundary={prev_char_is_boundary}')
        if not prev_char_is_boundary:
          return s
      if j < (length - 1):
        next_char = s[j + 1]
        next_char_is_boundary = char_util.is_word_boundary(next_char, underscore = underscore)
        #print(f'next_char={next_char} next_char_is_boundary={next_char_is_boundary}')
        if not next_char_is_boundary:
          return s
    
    left = s[:i]
    right = s[j + 1:]
    return left + replacement + right
      
  @classmethod
  def replace_all(clazz, s, src_string, dst_string, word_boundary = True, underscore = False):
    'Replace src_string with dst_string optionally respecting word boundaries.'
    check.check_string(s)
    check.check_string(src_string)
    check.check_string(dst_string)
    check.check_bool(word_boundary)
    check.check_bool(underscore)

    indeces = [ i for i in clazz.find_all(s, src_string) ]
    rindeces = reversed(indeces)
    n = len(src_string)
    for i in reversed(indeces):
      s = clazz.replace_span(s, i, n, dst_string,
                             word_boundary = word_boundary,
                             underscore = underscore)
    return s
  
  @classmethod
  def is_string(clazz, s):
    'Return True if s is a string.'
    return compat.is_string(s)
    
  @classmethod
  def is_char(clazz, s):
    'Return True if s is 1 character.'
    return clazz.is_string(s) and len(s) == 1

  @classmethod
  def is_ascii(clazz, s):
    'Return True if s is ascii.'
    try:
      s.decode('ascii')
      return True
    except Exception as ex:
      return False

  @classmethod
  def replace_punctuation(clazz, s, replacement):
    'Replace punctuation in s with replacement.'
    buf = StringIO()
    for c in s:
      if c in string.punctuation:
        if replacement:
          buf.write(replacement)
      else:
        buf.write(c)
    return buf.getvalue()

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
  def reverse(clazz, s):
    return ''.join(reversed(s))

  @classmethod
  def strip_ends(clazz, s, strip_head = False, strip_tail = False):
    if strip_head and strip_tail:
      return s.strip()
    elif strip_head:
      return s.lstrip()
    elif strip_tail:
      return s.rstrip()
    return s

  @classmethod
  def insert(clazz, s, what, index):
    'Insert what into s at index'
    return s[:index] + what + s[index:]

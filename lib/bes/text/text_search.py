#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.system.check import check
from bes.compat.StringIO import StringIO

from .word_boundary import word_boundary

class text_search(object):
  'Class to deal with text search and replace'

  _span = namedtuple('_span', 'start, end')

  @classmethod
  def find_all_word_boundary(clazz, text, sub_string, boundary_chars = None):
    'Returns a list of of all the spans containing sub_string in text'
    check.check_string(text)
    check.check_string(sub_string)
    check.check_set(boundary_chars, allow_none = True)

    boundary_chars = boundary_chars or word_boundary.CHARS_UNDERSCORE
    return [ span for span in clazz._do_find_all(text, sub_string, boundary_chars) ]
  
  @classmethod
  def find_all(clazz, text, sub_string):
    'Returns a list of of all the spans containing sub_string in text'
    check.check_string(text)
    check.check_string(sub_string)

    return [ span for span in clazz._do_find_all(text, sub_string, None) ]

  @classmethod
  def _do_find_all(clazz, text, sub_string, boundary_chars):
    sub_string_length = len(sub_string)
    i = 0
    while True:
      i = text.find(sub_string, i)
      if i < 0:
        return
      start = i
      end = i + sub_string_length - 1
      i += sub_string_length
      if boundary_chars != None:
        do_yield = word_boundary.word_has_boundary(text, start, end, boundary_chars = boundary_chars)
      else:
        do_yield = True
      if do_yield:
        yield clazz._span(start, end)

  @classmethod
  def replace_span(clazz, s, i, n, replacement):
    'Replace a span of text in s starting at i with a length of n'
    check.check_string(s)
    check.check_int(i)
    check.check_int(n)
    check.check_string(replacement)

    if i < 0:
      raise ValueError('i should be greater than 0')
    length = len(s)
    if i >= len(s):
      raise ValueError(f'n should be less than the length of s - {length}')
    if n < 1:
      raise ValueError('n should be at least 1')
    
    j = i + n - 1
    assert j >= i

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
  
'''      
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
'''

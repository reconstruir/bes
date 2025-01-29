#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import string

from bes.system.check import check
from bes.compat.StringIO import StringIO

from .text_search import text_search
from .text_span import text_span

class text_replace(object):
  'Class to deal with text replace'

  @classmethod
  def replace_all(clazz, text, src_string, dst_string,
                  word_boundary = False, word_boundary_chars = None,
                  case_insensitive = False):
    'Replace src_string with dst_string optionally respecting word boundaries.'
    check.check_string(text)
    check.check_string(src_string)
    check.check_string(dst_string)
    check.check_bool(word_boundary)
    check.check_set(word_boundary_chars, allow_none = True)

    spans = text_search.find_all(text,
                                 src_string,
                                 word_boundary = word_boundary,
                                 word_boundary_chars = word_boundary_chars,
                                 case_insensitive = case_insensitive)
    if not spans:
      return text
    last_start = 0
    buf = StringIO()
    last_span = None
    for span in spans:
      left = text[last_start : span.start]
      if left:
        buf.write(left)
      buf.write(dst_string)
      last_start = span.end + 1
      last_span = span
    if last_span:
      right = text[last_span.end + 1:]
      buf.write(right)
    return buf.getvalue()

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
  def replace(clazz,
              s,
              replacements,
              word_boundary = False,
              word_boundary_chars = None,
              case_insensitive = False):
    'Replace all instances of dict d in string s.'
    check.check_string(s)
    check.check_dict(replacements, check.STRING_TYPES, check.STRING_TYPES)
    check.check_bool(word_boundary)
    check.check_set(word_boundary_chars, allow_none = True)
    check.check_bool(case_insensitive)

    for src_string, dst_string in replacements.items():
      s = clazz.replace_all(s, src_string, dst_string,
                            word_boundary = word_boundary,
                            word_boundary_chars = word_boundary_chars,
                            case_insensitive = case_insensitive)
    return s

  @classmethod
  def replace_span(clazz, text, span, replacement):
    'Replace text span with replacement.'
    check.check_string(text)
    check.check_text_span(span)
    check.check_string(replacement)

    left = text[0:span.start]
    right = text[span.end:]
    return left + replacement + right
    

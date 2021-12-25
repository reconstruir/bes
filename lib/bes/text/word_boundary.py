#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import string

from bes.system.check import check

class word_boundary(object):

  # Default word boundary behavior in python regular expressions does
  # does not treat the underscore as a word boundary character.  So the
  # default here (BOUNDARY_CHARS) matches that behavior.
  CHARS_UNDERSCORE = set(string.whitespace) | set(string.punctuation)
  CHARS = CHARS_UNDERSCORE - set('_')
  
  @classmethod
  def word_has_boundary(clazz, text, start, end, boundary_chars = None):
    check.check_string(text)
    check.check_int(start)
    check.check_int(end)
    check.check_set(boundary_chars, allow_none = True)

    boundary_chars = boundary_chars or clazz.CHARS
    
    if start >= 1:
      prev_char = text[start - 1]
      prev_char_is_boundary = prev_char in boundary_chars
      #print(f'prev_char={prev_char} prev_char_is_boundary={prev_char_is_boundary}')
      if not prev_char_is_boundary:
        return False
    if end < (len(text) - 1):
      next_char = text[end + 1]
      next_char_is_boundary = next_char in boundary_chars
      #print(f'next_char={next_char} next_char_is_boundary={next_char_is_boundary}')
      if not next_char_is_boundary:
        return False
    return True

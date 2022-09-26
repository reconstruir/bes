#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import string

from collections import namedtuple

from bes.system.check import check
from bes.compat.StringIO import StringIO

from .word_boundary import word_boundary as word_boundary_module
from .text_span import text_span

class text_search(object):
  'Class to deal with text search and replace'

  @classmethod
  def find_all(clazz, text, sub_string, word_boundary = False, word_boundary_chars = None):
    'Returns a list of of all the spans containing sub_string in text'
    check.check_string(text)
    check.check_string(sub_string)
    check.check_bool(word_boundary)
    check.check_set(word_boundary_chars, allow_none = True)

    return [ span for span in clazz.find_all_generator(text,
                                                       sub_string,
                                                       word_boundary = word_boundary,
                                                       word_boundary_chars = word_boundary_chars) ]

  @classmethod
  def find_all_generator(clazz, text, sub_string, word_boundary = False, word_boundary_chars = None):
    check.check_string(text)
    check.check_string(sub_string)
    check.check_bool(word_boundary)
    check.check_set(word_boundary_chars, allow_none = True)

    word_boundary_chars = word_boundary_chars or word_boundary_module.CHARS
    sub_string_length = len(sub_string)
    i = 0
    while True:
      i = text.find(sub_string, i)
      if i < 0:
        return
      start = i
      end = i + sub_string_length - 1
      i += sub_string_length
      if word_boundary:
        assert word_boundary_chars
        do_yield = word_boundary_module.word_has_boundary(text, start, end, boundary_chars = word_boundary_chars)
      else:
        do_yield = True
      if do_yield:
        yield text_span(start, end)

  @classmethod
  def rfind_span(clazz, text, sub_string):
    check.check_string(text)
    check.check_string(sub_string)

    if sub_string == '':
      return None
    i = text.rfind(sub_string)
    if i < 0:
      return None
    return text_span(i, i + len(sub_string))

#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import re

from collections import namedtuple
from bes.common.check import check
from bes.common.string_util import string_util
from bes.compat.StringIO import StringIO
from bes.property.cached_property import cached_property
from bes.common.tuple_util import tuple_util

from .comments import comments

class text_line(namedtuple('text_line', 'line_number, text')):
  'Token used for line oriented text parser.  Keeps track of line text and line_number for error reporting.'
  
  CONTINUATION_CHAR = '\\'
  
  def __new__(clazz, line_number, text):
    check.check_int(line_number)
    check.check_string(text)
    return clazz.__bases__[0].__new__(clazz, line_number, text)

  def __str__(self):
    return '%s,%s' % (self.line_number, self.text)
  
  def __repr__(self):
    return str(self)

  @cached_property
  def ends_with_continuation(self):
    return self.text.strip().endswith(self.CONTINUATION_CHAR)
  
  def expand_continuations(self, indent = 0, keep_continuation = False):
    if not self.CONTINUATION_CHAR in self.text:
      return [ self ]
    indent_str = ' ' * indent
    texts = self.text.strip().split(self.CONTINUATION_CHAR)
    texts = [ text for text in texts if text ]
    result = []
    last_text_index = len(texts) - 1
    for i, text in enumerate(texts):
      if keep_continuation and i < last_text_index:
        text = '{}{}'.format(text, self.CONTINUATION_CHAR)
      if i != 0:
        text = '{}{}'.format(indent_str, text)
      new_line = text_line(self.line_number + i, text)
      result.append(new_line)
    return result
  
  @cached_property
  def text_no_comments(self):
    return comments.strip_line(self.text, strip_tail = True)

  @cached_property
  def stripped_text(self):
    return self.text.strip()
  
  @classmethod
  def merge(clazz, lines):
    'Merge a sequence of lines into one.  Continuation flags are cleared'
    buf = StringIO()
    for line in lines:
      text = string_util.remove_tail(line.text, clazz.CONTINUATION_CHAR)
      buf.write(text)
    return text_line(lines[0].line_number, buf.getvalue())

  def get_text(self, strip_comments = False, strip_text = False):
    if strip_comments:
      text = self.text_no_comments
    else:
      text = self.text
    if strip_text:
      text = text.strip()
    return text

  @cached_property
  def empty(self):
    return self.text_is_empty(strip_comments = False)
  
  @cached_property
  def empty_no_comments(self):
    return self.text_is_empty(strip_comments = True)
  
  def text_is_empty(self, strip_comments = False):
    return self.get_text(strip_comments = strip_comments, strip_text = True) == ''

  def clone(self, mutations = None):
    return tuple_util.clone(self, mutations = mutations)
  
  def clone_stripped(self):
    return self.clone(mutations = { 'text': self.text.strip() })

  def clone_line_number(self, line_number):
    return self.clone(mutations = { 'line_number': line_number })

  @cached_property
  def indent_length(self):
    count = 0
    for c in self.text:
      if c == ' ':
        count += 1
      elif c == '\t':
        count += 2
      else:
        break
    return count
  
check.register_class(text_line)

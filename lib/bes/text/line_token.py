#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from bes.common import string_util
from bes.compat import StringIO
from .comments import comments

class line_token(namedtuple('line_token', 'line_number,text')):

  CONTINUATION_CHAR = '\\'
  
  def __new__(clazz, line_number, text):
    return clazz.__bases__[0].__new__(clazz, line_number, text)

  def __str__(self):
    return '%s,%s' % (self.line_number, self.text)
  
  def __repr__(self):
    return '%s,%s' % (self.line_number, self.text)

  @property
  def has_continuation(self):
    return self.text.strip().endswith(self.CONTINUATION_CHAR)
  
  def get_text(self, strip_comments = False):
    if not strip_comments:
      return self.text
    return comments.strip_line(self.text, strip = True)

  @classmethod
  def merge(clazz, lines):
    'Merge a sequence of lines into one.  Continuation flags are cleared'
    buf = StringIO()
    for line in lines:
      text = string_util.remove_tail(line.text, clazz.CONTINUATION_CHAR)
      buf.write(text)
    return clazz(lines[0].line_number, buf.getvalue())

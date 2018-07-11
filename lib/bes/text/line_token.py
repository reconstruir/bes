#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from bes.common import check, string_util
from bes.compat import StringIO
from .comments import comments

class line_token(namedtuple('line_token', 'line_number,text')):
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

  @property
  def has_continuation(self):
    return self.text.strip().endswith(self.CONTINUATION_CHAR)
  
  @property
  def text_no_comments(self):
    return comments.strip_line(self.text, strip_tail = True)

  @classmethod
  def merge(clazz, lines):
    'Merge a sequence of lines into one.  Continuation flags are cleared'
    buf = StringIO()
    for line in lines:
      text = string_util.remove_tail(line.text, clazz.CONTINUATION_CHAR)
      buf.write(text)
    return clazz(lines[0].line_number, buf.getvalue())

  def get_text(self, strip_comments = False, strip_text = False):
    if strip_comments:
      text = self.text_no_comments
    else:
      text = self.text
    if strip_text:
      text = text.strip()
    return text
  
  def text_is_empty(self):
    return self.get_text(strip_text = True) == ''
  
  def clone_stripped(self):
    return line_token(self.line_number, self.text.strip())
  
check.register_class(line_token)

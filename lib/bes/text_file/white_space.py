#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.compat.StringIO import StringIO

class white_space(object):
  'Deal with white spaces.'
      
  @classmethod
  def shorten_multi_line_spaces(clazz, text):
    lines = text.split('\n')
    for i, line in enumerate(lines):
      if line.isspace():
        lines[i] = ''
    return '\n'.join(lines)

  @classmethod
  def count_leading_spaces(clazz, text):
    count = 0
    for c in text:
      if c.isspace():
        count += 1
      else:
        break
    return count

  @classmethod
  def escape_white_space(clazz, text):
    last_char = None
    buf = StringIO()
    for c in text:
      is_escaping = last_char == '\\'
      if c.isspace() and not is_escaping:
        buf.write('\\')
      buf.write(c)
      last_char = c
    return buf.getvalue()

  @classmethod
  def strip_head_new_lines(clazz, text):
    n = clazz._count_newlines(text)
    if n:
      return text[n:]
    return text
  
  @classmethod
  def strip_tail_new_lines(clazz, text):
    n = clazz._count_newlines(reversed(text))
    if n:
      return text[0:-n]
    return text
  
  @classmethod
  def strip_new_lines(clazz, text):
    text = clazz.strip_head_new_lines(text)
    return clazz.strip_tail_new_lines(text)
  
  @classmethod
  def _count_newlines(clazz, it):
    count = 0
    for c in it:
      if c == '\n':
        count += 1
      else:
        break
    return count

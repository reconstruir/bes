#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import string_util
from bes.compat import StringIO

from .string_lexer import string_lexer

class comments(object):

  @classmethod
  def strip_line(clazz, text, strip_head = False, strip_tail = False):
    'Strip comments from one line.'
    buf = StringIO()
    for token in string_lexer.tokenize(text, 'comments_strip_line', options = string_lexer.KEEP_QUOTES):
      if token.token_type not in [ string_lexer.TOKEN_DONE, string_lexer.TOKEN_COMMENT ]:
        buf.write(token.value)
    return string_util.strip_ends(buf.getvalue(), strip_head = strip_head, strip_tail = strip_tail)

  @classmethod
  def strip_in_lines(clazz, s, strip_head = False, strip_tail = False, remove_empties = False):
    'Strip comments from multiple lines.'
    lines = s.split('\n')
    stripped_lines = [ clazz.strip_line(line, strip_head = strip_head, strip_tail = strip_tail) for line in lines ]
    if remove_empties:
      stripped_lines = [ line for line in stripped_lines if line ]
    return '\n'.join(stripped_lines)

  @classmethod
  def strip_muti_line_comment(clazz, s, comment_head, comment_tail, replace = False):
    'Strip multi line spanning comments.'
    result = s
    while True:
      #print('result1: %s' % (result))
      start = result.find(comment_head)
      #print('start: %s' % (start))
      if start < 0:
        break
      end = result.find(comment_tail, start + len(comment_head))
      if end < 0:
        raise ValueError('Missing comment_tail')
      if replace:
        part = result[start:end + len(comment_tail)]
        spacified_part = clazz._spacify(part)
        result = result[0:start] + spacified_part + result[end + len(comment_tail):]
      else:
        result = result[0:start] + result[end + len(comment_tail):]
      #print('result2: %s' % (result))
    return result

  @classmethod
  def _spacify(clazz, s):
    buf = StringIO()
    for c in s:
      if c == '\n':
        buf.write(c)
      else:
        buf.write(' ')
    return buf.getvalue()

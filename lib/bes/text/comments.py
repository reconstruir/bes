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
  def strip_multi_line(clazz, s, strip_head = False, strip_tail = False, remove_empties = False):
    'Strip comments from multiple lines.'
    lines = s.split('\n')
    stripped_lines = [ clazz.strip_line(line, strip_head = strip_head, strip_tail = strip_tail) for line in lines ]
    if remove_empties:
      stripped_lines = [ line for line in stripped_lines if line ]
    return '\n'.join(stripped_lines)

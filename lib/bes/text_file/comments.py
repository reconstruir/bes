#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.string_util import string_util
from bes.compat.StringIO import StringIO

from .string_lexer import string_lexer

class comments(object):

  @classmethod
  def strip_line(clazz, text, allow_quoted = True, strip_head = False, strip_tail = False):
    'Strip comments from one line.'
    if allow_quoted:
      return clazz._strip_line_allow_quoted(text, strip_head = strip_head, strip_tail = strip_tail)
    else:
      return clazz._strip_line_disallow_quoted(text, strip_head = strip_head, strip_tail = strip_tail)

  @classmethod
  def _strip_line_allow_quoted(clazz, text, strip_head = False, strip_tail = False):
    'Strip comments from one line allowing for # to appear in quoted strings .'
    buf = StringIO()
    for token in string_lexer.tokenize(text, 'comments_strip_line', options = string_lexer.KEEP_QUOTES):
      if token.token_type not in [ string_lexer.TOKEN_DONE, string_lexer.TOKEN_COMMENT ]:
        buf.write(token.value)
    return string_util.strip_ends(buf.getvalue(), strip_head = strip_head, strip_tail = strip_tail)

  @classmethod
  def _strip_line_disallow_quoted(clazz, text, strip_head = False, strip_tail = False):
    'Strip comments from one line disallowing # to appear in quoted strings but much faster.'
    last_char = None
    buf = StringIO()
    found = False
    for c in text:
      is_escaping = last_char == '\\'
      if c == '#' and not is_escaping:
        found = True
        break
      if c != '\\':
        buf.write(c)
      last_char = c
    text = buf.getvalue()
    return string_util.strip_ends(text, strip_head = strip_head, strip_tail = strip_tail)

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
    '''
    Strip multi line spanning comments with the form:
    ##[apple 
    kiwi
    melon
    lemon
    ]##
    '''
    result = s
    find_start_index = 0
    while True:
      start = result.find(comment_head, find_start_index)
      if start < 0:
        break
      if start > 0 and s[start - 1] == '#':
        find_start_index = start + len(comment_head) + 1
        continue
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

  @classmethod
  def line_is_comment(clazz, text):
    'Return True if text is a comment.'
    return text.strip().startswith('#')

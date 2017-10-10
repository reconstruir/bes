#!/usr/bin/env python
#-*- coding:utf-8 -*-

from .string_lexer import string_lexer as lexer
from bes.compat import StringIO

class text_fit(object):
  'Fit text into bounded areas.'

  @classmethod
  def fit_text(clazz, text, width):
    lines = []
    for line in text.split('\n'):
      lines.extend(clazz.fit_line(text, width))
    return lines
      
  @classmethod
  def fit_line(clazz, text, width):
    assert '\n' not in text
    lines = []
    buf = StringIO()
    
    for token in lexer.tokenize(text, 'text_fit', options = lexer.KEEP_QUOTES | lexer.IGNORE_COMMENTS):
      if token.token_type == lexer.TOKEN_SPACE:
        if (buf.tell() + len(token.value)) > width:
          lines.append(buf.getvalue().strip())
          buf = StringIO()
        else:
          buf.write(token.value)
      if token.token_type == lexer.TOKEN_STRING:
        if (buf.tell() + len(token.value)) > width:
          lines.append(buf.getvalue().strip())
          buf = StringIO()
        buf.write(token.value)
      elif token.token_type == lexer.TOKEN_DONE:
        if buf.tell() > 0:
          lines.append(buf.getvalue().strip())
    return lines

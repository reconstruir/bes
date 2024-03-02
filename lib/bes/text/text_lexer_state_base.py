#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..common.string_util import string_util
from ..system.log import log

from .text_lexer_error import text_lexer_error

class text_lexer_state_base(object):

  EOS = '\0'
  
  def __init__(self, lexer):
    self.name = self.__class__.__name__[1:]
    #tag = f'{lexer.__class__.__name__}.{self.name}'
    tag = self.name[-20:]
    log.add_logging(self, tag = tag)
    self.lexer = lexer
  
  def handle_char(self, c):
    cs = self.char_to_string(c)
    raise RuntimeError(f'unhandled handle_char |{cs}| in state {self.name}')

  def log_handle_char(self, c):
    try:
      buffer_value = string_util.quote(self.lexer.buffer_value())
    except AttributeError as ex:
      buffer_value = 'None'
    attrs = self._make_log_attributes(c)
    self.log_d(f'handle_char: {attrs}')
  
  def _make_log_attributes(self, c, include_state = True):
    attributes = []
    if include_state:
      attributes.append(f'state={self.name}')
    cs = self.char_to_string(c)
    attributes.append(f'c=|{cs}|')
    try:
      bs = string_util.quote(self.lexer.buffer_value())
      attributes.append(f'buffer={bs}')
    except AttributeError as ex:
      attributes.append('buffer=None')
    attributes.append('is_escaping={self.lexer.is_escaping}')
    return ' '.join(attributes)

  @classmethod
  def char_to_string(clazz, c):
    if c == clazz.EOS:
      return 'EOS'
    else:
      return c

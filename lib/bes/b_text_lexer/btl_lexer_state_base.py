#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..common.string_util import string_util
from ..system.log import log
from ..system.check import check

from .btl_lexer_error import btl_lexer_error
from .btl_lexer_token import btl_lexer_token

class btl_lexer_state_base(object):

  EOS = '\0'
  
  def __init__(self, lexer):
    self.name = self.__class__.__name__
    tag = f'{lexer.__class__.__name__}.{self.name}'
    log.add_logging(self, tag = tag)
    self._lexer = lexer

  @property
  def position(self):
    return self._lexer.position

  @property
  def lexer(self):
    return self._lexer
    
  def char_in(self, c, char_name):
    check.check_string(c)
    check.check_string(char_name)
    
    return ord(c) in self._lexer.desc.char_map[char_name].chars
  
  def handle_char(self, c):
    cs = self.char_to_string(c)
    raise RuntimeError(f'unhandled handle_char |{cs}| in state {self.name}')

  def log_handle_char(self, c):
    try:
      buffer_value = string_util.quote(self._lexer.buffer_value())
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
      bs = string_util.quote(self._lexer.buffer_value())
      attributes.append(f'buffer={bs}')
    except AttributeError as ex:
      attributes.append('buffer=None')
    return ' '.join(attributes)

  @classmethod
  def char_to_string(clazz, c):
    if c == clazz.EOS:
      return 'EOS'
    else:
      return c

#  def make_token(self, name, value, position):
#    return btl_lexer_token(name, value, position)

  def make_token(self, name):
    return btl_lexer_token(name, self.buffer_value(), self._lexer._buffer_position)
  
  def buffer_reset(self, c = None):
    self._lexer.buffer_reset(c = c)

  def buffer_write(self, c):
    self._lexer.buffer_write(c)

  def buffer_value(self):
    return self._lexer.buffer_value()


#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..common.string_util import string_util
from ..system.log import log
from ..system.check import check

from .btl_lexer_error import btl_lexer_error
from .btl_lexer_token import btl_lexer_token

class btl_lexer_state_base(object):

  EOS = '\0'
  
  def __init__(self, lexer, name, log_tag):
    check.check_string(name)
    check.check_string(log_tag)
    
    self.name = name
    log.add_logging(self, tag = log_tag)
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
    attrs = self._make_log_attributes(c)
    self.log_d(f'{self.name}: handle_char: {attrs}')
  
  def _make_log_attributes(self, c):
    attributes = []
    cs = self.char_to_string(c)
    attributes.append(f'c=▒{cs}▒')
    try:
      bs = self._lexer.buffer_value()
      attributes.append(f'buffer=▒{bs}▒')
    except AttributeError as ex:
      attributes.append('buffer=None')
    return ' '.join(attributes)

  @classmethod
  def char_to_string(clazz, c):
    if c == clazz.EOS:
      return 'EOS'
    else:
      return c

  def make_token(self, name):
    return btl_lexer_token(name, self.buffer_value(), self._lexer._buffer_position)
  
  def buffer_reset(self):
    self._lexer.buffer_reset()

  def buffer_write(self, c):
    self._lexer.buffer_write(c)

  def buffer_value(self):
    return self._lexer.buffer_value()


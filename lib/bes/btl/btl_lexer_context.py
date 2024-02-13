#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import io

from ..system.check import check
from ..system.log import log

from .btl_lexer_options import btl_lexer_options
from .btl_point import btl_point

class btl_lexer_context(object):

  def __init__(self, lexer, log_tag, text, source, options):
    check.check_btl_lexer(lexer)
    check.check_string(log_tag)
    check.check_string(text)
    check.check_string(source, allow_none = True)
    check.check_btl_lexer_options(options, allow_none = True)

    log.add_logging(self, tag = log_tag)
    
    self._text = text
    self._source = source or '<unknown>'
    self._options = options or btl_lexer_options()
    self._state = lexer.start_state
    self._last_char = None
    self._last_position = btl_point(0, 1)
    self._position = btl_point(0, 1)
    self._last_position = None
    self._buffer = None
    self._buffer_start_position = None
    self.buffer_reset()

  @property
  def text(self):
    return self._text

  @property
  def source(self):
    return self._source

  @property
  def options(self):
    return self._options

  @property
  def state(self):
    return self._state

  @state.setter
  def state(self, state):
    self._state = state

  @property
  def last_char(self):
    return self._last_char

  @last_char.setter
  def last_char(self, last_char):
    self._last_char = last_char
    
  @property
  def position(self):
    return self._position

  @property
  def last_position(self):
    return self._last_position

  def update_position(self, c):
    self._last_position = self._position
    if c in ( '\n', '\r\n' ):
      new_position = btl_point(0, self._last_position.y + 1)
    else:
      new_position = btl_point(self._last_position.x + len(c), self._last_position.y)
    self._position = new_position

  @property
  def buffer_start_position(self):
    return self._buffer_start_position
    
  def buffer_reset(self):
    old_buffer_position = btl_point(*self._buffer_start_position) if self._buffer_start_position != None else 'None'
    old_buffer_value = self.buffer_value()
    self._buffer = io.StringIO()
    if self._buffer_start_position == None:
      self._buffer_start_position = btl_point(1, 1)
    self._buffer_start_position = btl_point(*self._position)
    self.log_d(f'lexer: buffer_reset: old_value="{old_buffer_value}" old_position={old_buffer_position} new_position={self._buffer_start_position} pos={self._position}')

  def buffer_write(self, c):
    check.check_string(c)
    
    old_buffer_position = btl_point(*self._buffer_start_position)
    old_value = self.buffer_value()
    assert c != '\0'
    self._buffer.write(c)
    if len(old_value) == 0:
      self._buffer_start_position = btl_point(*self._position)
    cs = 'caca' #self._state.char_to_string(c)
    self.log_d(f'lexer: buffer_write: c="{cs}" old_position={old_buffer_position} new_position={self._buffer_start_position} pos={self._position}')    

  def buffer_value(self):
    if self._buffer == None:
      return None
    return self._buffer.getvalue()
    
check.register_class(btl_lexer_context, include_seq = False)

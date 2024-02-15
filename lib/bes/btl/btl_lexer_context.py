#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import io
import os

from ..system.check import check
from ..system.log import log
from ..text.line_numbers import line_numbers

from .btl_document_position import btl_document_position
from .btl_lexer_options import btl_lexer_options
from .btl_lexer_token import btl_lexer_token
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
    self._last_position = btl_document_position(1, 0)
    self._position = btl_document_position(1, 0)
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

  def advance_position(self, c):
    self._last_position = self._position
    self._position = self._position.advanced(c)

  @property
  def buffer_start_position(self):
    return self._buffer_start_position
    
  def buffer_reset(self):
    old_buffer_position = btl_document_position(*self._buffer_start_position) if self._buffer_start_position != None else 'None'
    old_buffer_value = self.buffer_value()
    self._buffer = io.StringIO()
    if self._buffer_start_position == None:
      self._buffer_start_position = btl_document_position(1, 1)
    else:
      self._buffer_start_position = btl_document_position(*self._position)
    self.log_d(f'lexer: buffer_reset: old_value="{old_buffer_value}" old_position={old_buffer_position} new_position={self._buffer_start_position} pos={self._position}')

  def buffer_write(self, c):
    check.check_string(c)
    
    old_buffer_position = btl_document_position(*self._buffer_start_position)
    old_value = self.buffer_value()
    assert c != '\0'
    self._buffer.write(c)
    if len(old_value) == 0:
      self._buffer_start_position = btl_point(*self._position)
    cs = btl_lexer_token.make_debug_str(c)
    self.log_d(f'lexer: buffer_write: c="{cs}" old_position={old_buffer_position} new_position={self._buffer_start_position} pos={self._position}')    

  def buffer_value(self):
    if self._buffer == None:
      return None
    return self._buffer.getvalue()

  def make_error_text(self, text, message):
    check.check_string(text)
    check.check_string(message)

    if not text:
      return ''

    NUM_CONTEXT_LINES = 5

    position = self.position or btl_document_position(666, 666)
    
    numbered_text = line_numbers.add_line_numbers(text, delimiter = '|')
    delim_col = numbered_text.find('|')
    lines = numbered_text.splitlines()
    top = lines[0:position.line][-NUM_CONTEXT_LINES:]
    bottom = lines[position.line:][0:NUM_CONTEXT_LINES]
    indent = ' ' * (position.column + delim_col)
    marker = f'{indent}^^^ {message}'
    error_lines = top + [ marker ] + bottom
    return os.linesep.join(error_lines).rstrip()
  
check.register_class(btl_lexer_context, include_seq = False)

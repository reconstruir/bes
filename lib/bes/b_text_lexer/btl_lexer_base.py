#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import io

from ..system.log import log
from ..system.check import check
from ..common.point import point

from .btl_lexer_error import btl_lexer_error
from .btl_lexer_token_list import btl_lexer_token_list
from .btl_desc import btl_desc

class btl_lexer_base(object):

  EOS = '\0'
  
  def __init__(self, log_tag, desc_text, token, states, source = None):
    check.check_string(log_tag)
    check.check_string(desc_text)
    check.check_string(source, allow_none = True)
    
    self._log_tag = log_tag
    log.add_logging(self, tag = self._log_tag)
    self._source = source or '<unknown>'
    self._desc = btl_desc.parse_text(desc_text, source = self._source)
    self._token = token
    self._states = states
    self._buffer = None
    self._last_char = None
    self._state = self._find_state(self._desc.header.start_state)
    self._position = point(1, 1)
    self._buffer_position = point(1, 1)
    self.buffer_reset()
    self._max_state_name_length = max([ len(state.name) for state in self._states.values() ])

  @property
  def position(self):
    return self._position

  @property
  def buffer_position(self):
    return self._buffer_position
  
  @property
  def desc(self):
    return self._desc

  @property
  def token(self):
    return self._token

  @property
  def log_tag(self):
    return self._log_tag
  
  def _find_state(self, state_name):
    return self._states[state_name]
  
  def change_state(self, new_state_name, c):
    check.check_string(new_state_name, allow_none = True)
    check.check_string(c)

    assert new_state_name
    #import pprint
    #print(pprint.pformat(self._states))
    
    new_state = self._find_state(new_state_name)
    if new_state == self._state:
      return
#    x = self._state.name.zfill(self._max_state_name_length)
    attrs = new_state._make_log_attributes(c)
    max_length = self._max_state_name_length
    msg = f'lexer: transition: ▒{self._state.name:>{max_length}} -> {new_state.name:<{max_length}}▒ {attrs}'
    self.log_d(msg)
    self._state = new_state

  def buffer_reset(self, c = None):
    self._buffer = io.StringIO()
    if c:
      self.buffer_write(c)
    self._buffer_position = self._position

  def buffer_write(self, c):
    check.check_string(c)
    assert c != self.EOS
    self._buffer.write(c)

  def buffer_value(self):
    return self._buffer.getvalue()

  def run(self, text):
    check.check_string(text)
    
    self.log_d(f'lexer: run: text=\"{text}\"')
    
    assert self.EOS not in text
    self._position = point(0, 1)
    for c in self._chars_plus_eos(text):
      #self._is_escaping = self._last_char == '\\'
      #should_handle_char = (self._is_escaping and c == '\\') or (c != '\\')
      #if should_handle_char:
      tokens = self._state.handle_char(c)
      for token in tokens:
        self.log_d(f'lexer: run: new token: {token}')
        yield token
      self._last_char = c
      if c == '\n':
        self._position = point(self._position.x, self._position.y + 1)
      else:
        self._position = point(self._position.x + 1, self._position.y)

    end_state = self._find_state(self._desc.header.end_state)
    assert self._state == end_state

  def tokenize(self, text):
    return btl_lexer_token_list([ token for token in self.run(text) ])
    
  @classmethod
  def _chars_plus_eos(self, text):
    for c in text:
      yield c
    yield self.EOS

  def make_token(self, name):
    check.check_string(name)
    
    return btl_lexer_token(name, self.buffer_value(), self.buffer_position)
    

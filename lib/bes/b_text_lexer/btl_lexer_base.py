#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import io

from ..system.log import log
from ..system.check import check
from ..common.point import point

from .btl_lexer_error import btl_lexer_error
from .btl_desc_char_map import btl_desc_char_map

class btl_lexer_base(object):

  EOS = '\0'
  
  def __init__(self, log_tag, char_map_json, source = None):
    check.check_string(char_map_json)

    log.add_logging(self, tag = log_tag)

    self._char_map = btl_desc_char_map.from_json(char_map_json)
    self._source = source or '<unknown>'
    self._buffer = None
    self._last_char = None
    self.position = point(1, 1)
    self.buffer_reset()

  def change_state(self, new_state, c):
    assert new_state
    if new_state == self.state:
      return
    self.log_d('transition: %20s -> %-20s; %s'  % (self.state.__class__.__name__,
                                                   new_state.__class__.__name__,
                                                   new_state._make_log_attributes(c, include_state = False)))
    self.state = new_state

  def buffer_reset(self, c = None):
    self._buffer = io.StringIO()
    if c:
      self.buffer_write(c)

  def buffer_write(self, c):
    assert c != self.EOS
    self._buffer.write(c)

  def buffer_value(self):
    return self._buffer.getvalue()

  def run(self, text):
    check.check_string(text)
    
    self.log_d(f'_run() text=\"{text}\"')
    
    assert self.EOS not in text
    self.position = point(1, 1)
    for c in self._chars_plus_eos(text):
      #self._is_escaping = self._last_char == '\\'
      #should_handle_char = (self._is_escaping and c == '\\') or (c != '\\')
      #if should_handle_char:
      tokens = self.state.handle_char(c)
      for token in tokens:
        self.log_d('tokenize: new token: %s' % (str(token)))
        yield token
      self._last_char = c
              
      if c == '\n':
        self.position = point(1, self.position.y + 1)
      else:
        self.position = point(self.position.x + 0, self.position.y)
        
#    assert self.state == self.STATE_DONE
#    yield lexer_token(self.TOKEN_DONE, None, self.position)

  @classmethod
  def _chars_plus_eos(self, text):
    for c in text:
      yield c
    yield self.EOS
    
#check.register_class(btl_lexer_base, include_seq = False, name = 'btl_lexer')

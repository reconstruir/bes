#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import io

from ..system.log import log
from ..system.check import check
from ..common.point import point

from .btl_lexer_error import btl_lexer_error
from .btl_desc import btl_desc

class btl_lexer_base(object):

  EOS = '\0'
  
  def __init__(self, log_tag, desc_text, token, states, source = None):
    check.check_string(desc_text)

    log.add_logging(self, tag = log_tag)
    self._source = source or '<unknown>'
    self._desc = btl_desc.parse_text(desc_text, source = self._source)
    self._token = token
    self._states = states
    self._buffer = None
    self._last_char = None
    self._state = self._find_state(self._desc.header.start_state)
    self.position = point(1, 1)
    self.buffer_reset()

  @property
  def lexer(self):
    return self._lexer
    
  @property
  def desc(self):
    return self._desc

  @property
  def token(self):
    return self._token

  def _find_state(self, state_name):
    return self._states[state_name]
  
  def change_state(self, new_state_name, c):
    check.check_string(new_state_name, allow_none = True)
    if not new_state_name:
      return
    if check.is_int(c):
      c = chr(c)
    check.check_string(c)
    
    import pprint
    print(pprint.pformat(self._states))
    
    new_state = self._find_state(new_state_name)
    if new_state == self._state:
      return
    self.log_d('transition: %20s -> %-20s; %s'  % (self._state.__class__.__name__,
                                                   new_state.__class__.__name__,
                                                   new_state._make_log_attributes(c, include_state = False)))
    self._state = new_state

  def buffer_reset(self, c = None):
    self._buffer = io.StringIO()
    if c:
      self.buffer_write(c)

  def buffer_write(self, c):
    if check.is_int(c):
      c = chr(c)
    check.check_string(c)
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
      ord_c = ord(c)
      tokens = self._state.handle_char(ord_c)
      for token in tokens:
        self.log_d('tokenize: new token: %s' % (str(token)))
        yield token
      self._last_char = c
      if c == '\n':
        self.position = point(1, self.position.y + 1)
      else:
        self.position = point(self.position.x + 0, self.position.y)

    end_state = self._find_state(self._desc.header.end_state)
    assert self._state == end_state
        
  @classmethod
  def _chars_plus_eos(self, text):
    for c in text:
      yield c
    yield self.EOS
    
#check.register_class(btl_lexer_base, include_seq = False, name = 'btl_lexer')

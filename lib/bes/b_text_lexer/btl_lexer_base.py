#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.log import log
from ..system.check import check

from .btl_lexer_error import btl_lexer_error
from .btl_desc_char_map import btl_desc_char_map

class btl_lexer_base(object):

  def __init__(self, log_tag, char_map_json, source = None):
    check.check_string(char_map_json)
    
    log.add_logging(self, tag = log_tag)

    self._char_map = btl_desc_char_map.from_json(char_map_json)
    self._source = source or '<unknown>'
    self._buffer = None
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
    self._buffer = StringIO()
    if c:
      self.buffer_write(c)

  def buffer_write(self, c):
    assert c != self.EOS
    self._buffer.write(c)

  def buffer_value(self):
    return self._buffer.getvalue()
  
check.register_class(btl_lexer_base, include_seq = False, name = 'lexer')

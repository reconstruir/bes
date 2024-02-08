#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

import io

from ..system.log import log
from ..system.check import check
from ..common.point import point
from ..common.node import node as node_class

from .btl_parser_desc import btl_parser_desc
from .btl_parser_error import btl_parser_error
from .btl_parser_node import btl_parser_node
from .btl_parser_node_creator import btl_parser_node_creator

class btl_parser_base(object):

  EOS = '\0'
  
  def __init__(self, lexer, desc_text, states):
    check.check_btl_lexer(lexer)
    check.check_string(desc_text)
    
    self._lexer = lexer
    log.add_logging(self, tag = self._lexer.log_tag)
    self._desc = btl_parser_desc.parse_text(desc_text, source = lexer.source)
    self._states = states
    self._state = self._find_state(self._desc.header.start_state)
    self._max_state_name_length = max([ len(state.name) for state in self._states.values() ])
    self._node_creator = btl_parser_node_creator()

  @property
  def node_creator(self):
    return self._node_creator
    
  @property
  def lexer(self):
    return self._lexer
    
  @property
  def desc(self):
    return self._desc

  @property
  def log_tag(self):
    return self._lexer.log_tag
  
  def _find_state(self, state_name):
    return self._states[state_name]
  
  def change_state(self, new_state_name, token):
    check.check_string(new_state_name, allow_none = True)
    check.check_btl_lexer_token(token)

    if new_state_name == None:
      ts = token.to_debug_str()
      raise btl_parser_error(f'Cannot transition from state "{self._state.name}" to "None" for token "{ts}"')
    
    new_state = self._find_state(new_state_name)
    if new_state == self._state:
      return
    attrs = 'attrs' #new_state._make_log_attributes(c)
    max_length = self._max_state_name_length
    msg = f'lexer: transition: ▒{self._state.name:>{max_length}} -> {new_state.name:<{max_length}}▒ {attrs}'
    self.log_d(msg)
    self._state = new_state

  def buffer_reset(self):
    old_buffer_position = point(*self._buffer_start_position) if self._buffer_start_position != None else 'None'
    old_buffer_value = self.buffer_value()
    self._buffer = io.StringIO()
    if self._buffer_start_position == None:
      self._buffer_start_position = point(1, 1)
    self._buffer_start_position = point(*self._position)
    self.log_d(f'lexer: buffer_reset: old_value=▒{old_buffer_value}▒ old_position={old_buffer_position} new_position={self._buffer_start_position} pos={self._position}')

  def buffer_write(self, c):
    check.check_string(c)
    
    old_buffer_position = point(*self._buffer_start_position)
    old_value = self.buffer_value()
    assert c != self.EOS
    self._buffer.write(c)
    if len(old_value) == 0:
      self._buffer_start_position = point(*self._position)
    cs = self._state.char_to_string(c)
    self.log_d(f'lexer: buffer_write: c=▒{cs}▒ old_position={old_buffer_position} new_position={self._buffer_start_position} pos={self._position}')    

  def buffer_value(self):
    if self._buffer == None:
      return None
    return self._buffer.getvalue()

  def run(self, text):
    check.check_string(text)
    
    self.log_d(f'parser: run: text=\"{text}\"')

    for token in self._lexer.run(text):
      #attrs = self._state._make_log_attributes(c)
      ts = token.to_debug_str()
      self.log_d(f'parser: loop: token={ts}')
      old_state_name = self._state.name
      new_state_name = self._state.handle_token(token)
      self.change_state(new_state_name, token)

    end_state = self._find_state(self._desc.header.end_state)
    assert self._state == end_state

  @classmethod
  def OLD_chars_plus_eos(self, text):
    for c in text:
      yield c
    yield self.EOS

  @classmethod
  def _chars_plus_eos(self, text):
    n = len(text)
    skip_next_char = False
    for i, c in enumerate(text):
      if skip_next_char:
        skip_next_char = False
        continue
      next_c = None
      if n >= 2 and i < (n - 1):
        next_c = text[i + 1]
      yielded = False
      if next_c != None:
        if c == '\r' and next_c == '\n':
          yield '\r\n'
          skip_next_char = True
          yielded = True
      if not yielded:
        yield c
    yield self.EOS
    
  def make_token(self, name, args = None):
    check.check_string(name)
    check.check_dict(args, check.STRING_TYPES, check.STRING_TYPES, allow_none = True)

    token_args = self._make_token_args(name, args)
    
    assert self.buffer_start_position != None
    token_position = self.buffer_start_position
    buffer_value = self.buffer_value()
    type_hint = token_args.get('type_hint', None)
    if type_hint:
      if type_hint == 'h_line_break':
        token_position = point(self._last_position.x + 1, self._last_position.y)
      elif type_hint == 'h_done':
        token_position = None
        buffer_value = None
    token = btl_parser_node(name,
                            value = buffer_value,
                            position = token_position,
                            type_hint = type_hint)
    return token

  def _make_token_args(self, name, args):
    check.check_string(name)
    check.check_dict(args, check.STRING_TYPES, check.STRING_TYPES, allow_none = True)

    result = {}
    token_args = args or {}
    token_desc = self._desc.tokens.find_token(name)
    if not token_desc:
      raise btl_parser_error(f'No token description found: "{name}"')
    desc_args = token_desc.args or {}
    result.update(desc_args)
    result.update(token_args)
    return result
  
check.register_class(btl_parser_base, name = 'btl_parser', include_seq = False)

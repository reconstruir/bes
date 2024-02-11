#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import io

from ..system.log import log
from ..system.check import check
from ..common.point import point

from .btl_lexer_desc import btl_lexer_desc
from .btl_lexer_error import btl_lexer_error
from .btl_lexer_options import btl_lexer_options
from .btl_lexer_token import btl_lexer_token
from .btl_lexer_token_deque import btl_lexer_token_deque

class btl_lexer_base(object):

  EOS = '\0'
  
  def __init__(self, log_tag, desc_text, token, states, desc_source = None):
    check.check_string(log_tag)
    check.check_string(desc_text)
    check.check_string(desc_source, allow_none = True)
    
    self._log_tag = log_tag
    log.add_logging(self, tag = self._log_tag)
    self._desc_source = desc_source or '<unknown>'
    self._desc = btl_lexer_desc.parse_text(desc_text, source = self._desc_source)
    self._token = token
    self._states = states
    self._buffer = None
    self._last_char = None
    self._state = self._find_state(self._desc.header.start_state)
    self._max_state_name_length = max([ len(state.name) for state in self._states.values() ])
    self._position = point(1, 1)
    self._last_position = point(0, 1)
    self._buffer_start_position = None
    self.buffer_reset()

  @property
  def position(self):
    return self._position
  
  @property
  def desc_source(self):
    return self._desc_source

  @property
  def buffer_start_position(self):
    return self._buffer_start_position
  
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
  
  def change_state(self, new_state_name, c, options):
    check.check_string(new_state_name, allow_none = True)
    check.check_string(c)

    if new_state_name == None:
      cs = self._state.char_to_string(c)
      raise btl_lexer_error(f'Cannot transition from state "{self._state.name}" to "None" for char "{cs}"')
    
    new_state = self._find_state(new_state_name)
    if new_state == self._state:
      return
    attrs = new_state._make_log_attributes(c, options)
    max_length = self._max_state_name_length
    msg = f'lexer: transition: #{self._state.name:>{max_length}} -> {new_state.name:<{max_length}}# {attrs}'
    self.log_d(msg)
    self._state = new_state

  def buffer_reset(self):
    old_buffer_position = point(*self._buffer_start_position) if self._buffer_start_position != None else 'None'
    old_buffer_value = self.buffer_value()
    self._buffer = io.StringIO()
    if self._buffer_start_position == None:
      self._buffer_start_position = point(1, 1)
    self._buffer_start_position = point(*self._position)
    self.log_d(f'lexer: buffer_reset: old_value="{old_buffer_value}" old_position={old_buffer_position} new_position={self._buffer_start_position} pos={self._position}')

  def buffer_write(self, c):
    check.check_string(c)
    
    old_buffer_position = point(*self._buffer_start_position)
    old_value = self.buffer_value()
    assert c != self.EOS
    self._buffer.write(c)
    if len(old_value) == 0:
      self._buffer_start_position = point(*self._position)
    cs = self._state.char_to_string(c)
    self.log_d(f'lexer: buffer_write: c="{cs}" old_position={old_buffer_position} new_position={self._buffer_start_position} pos={self._position}')    

  def buffer_value(self):
    if self._buffer == None:
      return None
    return self._buffer.getvalue()

  def lex_generator(self, text, source = None, options = None):
    check.check_string(text)
    check.check_string(source, allow_none = True)
    check.check_btl_lexer_options(options, allow_none = True)
    
    source = source or '<unknown>'
    options = options or btl_lexer_options()
    self.log_d(f'lexer: run: source={source} options={options} text=\"{text}\"')

    if self.EOS in text:
      raise btl_lexer_error(f'Invalid text. NULL character (\\0) not allowed')
      
    self._position = point(0, 1)
    for c in self._chars_plus_eos(text):
      self._position = self._update_position(self._position, c)
      attrs = self._state._make_log_attributes(c, options)
      self.log_d(f'lexer: loop: {attrs} position={self._position}')
      old_state_name = self._state.name
      handle_char_result = self._state.handle_char(c, options)
      new_state_name = handle_char_result.new_state_name
      self.change_state(new_state_name, c, options)
      for token in handle_char_result.tokens:
        self.log_d(f'lexer: run: new token in state {old_state_name}: {token.to_debug_str()}')
        yield token
      self._last_char = c
      self._last_position = self._position

    end_state = self._find_state(self._desc.header.end_state)
    assert self._state == end_state

  def lex_all(self, text):
    return btl_lexer_token_deque([ token for token in self.lex_generator(text) ])
    
  @classmethod
  def _update_position(clazz, old_position, c):
    if c in ( '\n', '\r\n' ):
      new_position = point(0, old_position.y + 1)
    else:
      new_position = point(old_position.x + len(c), old_position.y)
    return new_position
    
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
    token = btl_lexer_token(name,
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
      raise btl_lexer_error(f'No token description found: "{name}"')
    desc_args = token_desc.args or {}
    result.update(desc_args)
    result.update(token_args)
    return result

check.register_class(btl_lexer_base, name = 'btl_lexer', include_seq = False)

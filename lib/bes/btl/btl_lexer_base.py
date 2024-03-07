#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..property.cached_class_property import cached_class_property
from ..system.check import check
from ..system.log import log

from abc import abstractmethod
from abc import ABCMeta

from .btl_document_position import btl_document_position
from .btl_lexer_context import btl_lexer_context
from .btl_lexer_desc import btl_lexer_desc
from .btl_lexer_error import btl_lexer_error
from .btl_lexer_options import btl_lexer_options
from .btl_lexer_runtime_error import btl_lexer_runtime_error
from .btl_lexer_token import btl_lexer_token
from .btl_lexer_token_list import btl_lexer_token_list

class btl_lexer_base(metaclass = ABCMeta):

  EOS = '\0'

  def __init__(self, log_tag, token, states):
    check.check_string(log_tag)
  
    self._log_tag = log_tag
    log.add_logging(self, tag = self._log_tag)
    self._states = states
    self._token = token
    self._max_state_name_length = max([ len(state.name) for state in self._states.values() ])

  @classmethod
  @abstractmethod
  def desc_source(clazz):
    raise NotImplementedError(f'desc_source')
  
  @classmethod
  @abstractmethod
  def desc_text(clazz):
    raise NotImplementedError(f'desc_text')

  @cached_class_property
  def desc(clazz):
    return btl_lexer_desc.parse_text(clazz.desc_text(), clazz.desc_source())
  
  @property
  def desc_source(self):
    return self._desc_source

  @property
  def token(self):
    return self._token

  @property
  def start_state(self):
    return self._find_state(self.desc.header.start_state)

  @property
  def end_state(self):
    return self._find_state(self.desc.header.end_state)
  
  def _find_state(self, state_name):
    return self._states[state_name]
  
  def _change_state(self, context, new_state_name, c):
    if new_state_name == None:
      cs = context.state.char_to_string(c)
      message = f'lexer: failed to transition from state "{context.state.name}" for char "{cs}"'
      raise btl_lexer_runtime_error(context, message)
    
    new_state = self._find_state(new_state_name)
    if new_state == context.state:
      return
    attrs = new_state._make_log_attributes(context, c)
    max_length = self._max_state_name_length
    msg = f' lexer: transition: {context.state.name} -> {new_state.name} {attrs}'
    self.log_i(msg)
    context.state = new_state

  def lex_generator(self, text, options = None):
    check.check_string(text)
    check.check_btl_lexer_options(options, allow_none = True)

    if self.EOS in text:
      raise btl_lexer_error(f'Invalid text. NULL character (\\0) not allowed')

    vm = self.desc.make_variable_manager(options.variables if options else {})
    char_map = self.desc.char_map.substituted_variables(vm)
    context = btl_lexer_context(self, self._log_tag, text, char_map, options)
    self.log_i(f' lexer: run: options={context.options}')
    self.log_d(f' lexer: run: text=\"{text}\"')

    for c in self._chars_plus_eos(text):
      old_position = context.position.clone()
      context.advance_position(c)
      attrs = context.state._make_log_attributes(context, c)
      self.log_i(f' lexer: loop: {attrs} old_position={old_position} new_position={context.position}')
      old_state_name = context.state.name
      handle_char_result = context.state.handle_char(context, c)
      new_state_name = handle_char_result.new_state_name
      self._change_state(context, new_state_name, c)
      for token in handle_char_result.tokens:
        self.log_i(f' lexer: run: new token in state {old_state_name}: {token.to_debug_str()}')
        yield token
      context.last_char = c

    if context.state != self.end_state:
      raise btl_lexer_error(f'The end state is incorrectly "{context.state.name}" instead of "{self.end_state.name}"')

  def lex_all(self, text, options = None):
    check.check_btl_lexer_options(options, allow_none = True)

    return btl_lexer_token_list([ token for token in self.lex_generator(text, options = options) ])
    
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
    
  def make_token(self, context, name):
    check.check_btl_lexer_context(context)
    check.check_string(name)

    token_args = self._make_token_args(name)
    
    assert context.buffer_start_position != None
    token_position = context.buffer_start_position
    buffer_value = context.buffer_value()
    type_hint = token_args.get('type_hint', None)
    if type_hint:
      if type_hint == 'h_line_break':
        token_position = context.last_position.moved_horizontal(1)
      elif type_hint == 'h_done':
        token_position = None
        buffer_value = None
    token = btl_lexer_token(name,
                            value = buffer_value,
                            position = token_position,
                            type_hint = type_hint)
    return token

  def _make_token_args(self, name):
    check.check_string(name)

    result = {}
    token_args = {}
    token_desc = self.desc.tokens.find_token(name)
    if not token_desc:
      raise btl_lexer_error(f'No token description found: "{name}"')
    desc_args = token_desc.args or {}
    result.update(desc_args)
    result.update(token_args)
    return result

check.register_class(btl_lexer_base, name = 'btl_lexer', include_seq = False)

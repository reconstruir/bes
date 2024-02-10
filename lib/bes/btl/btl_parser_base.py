#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.log import log
from ..system.check import check

from .btl_parser_desc import btl_parser_desc
from .btl_parser_error import btl_parser_error
from .btl_parser_node import btl_parser_node
from .btl_parser_node_creator import btl_parser_node_creator
from .btl_lexer_token_lines import btl_lexer_token_lines

class btl_parser_base(object):

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
    
  def run(self, text):
    check.check_string(text)
    
    self.log_d(f'parser: run: text=\"{text}\"')

    #btl_lexer_token_lines
    tokens = self._lexer.tokenize(text)
    
    for token in tokens:
      ts = token.to_debug_str()
      self.log_d(f'parser: loop: token={ts}')
      old_state_name = self._state.name
      new_state_name = self._state.handle_token(token)
      self.change_state(new_state_name, token)

    end_state = self._find_state(self._desc.header.end_state)
    assert self._state == end_state
    result = self._node_creator.get_root_node()
    return result

check.register_class(btl_parser_base, name = 'btl_parser', include_seq = False)

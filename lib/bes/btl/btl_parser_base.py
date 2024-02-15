#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from ..system.log import log
from ..system.check import check

from .btl_document_position import btl_document_position
from .btl_lexer_token_deque import btl_lexer_token_deque
from .btl_lexer_token_lines import btl_lexer_token_lines
from .btl_parser_context import btl_parser_context
from .btl_parser_desc import btl_parser_desc
from .btl_parser_error import btl_parser_error
from .btl_parser_node import btl_parser_node
from .btl_parser_node_creator import btl_parser_node_creator

class btl_parser_base(object):

  def __init__(self, log_tag, lexer, desc_text, states, desc_source = None):
    check.check_string(log_tag)
    check.check_btl_lexer(lexer)
    check.check_string(desc_text)
    check.check_string(desc_source, allow_none = True)

    self._log_tag = log_tag
    self._desc_source = desc_source or '<unknown>'
    self._lexer = lexer
    log.add_logging(self, tag = self._log_tag)
    self._desc = btl_parser_desc.parse_text(desc_text, source = self._desc_source)
    self._states = states
    self._max_state_name_length = max([ len(state.name) for state in self._states.values() ])

  @property
  def lexer(self):
    return self._lexer
    
  @property
  def desc_source(self):
    return self._desc_source

#  @property
#  def log_tag(self):
#    return self._lexer.log_tag
  
  @property
  def start_state(self):
    return self._find_state(self._desc.header.start_state)

  @property
  def end_state(self):
    return self._find_state(self._desc.header.end_state)
  
  def _find_state(self, state_name):
    return self._states[state_name]
  
  def _change_state(self, context, new_state_name, token):
    if new_state_name == None:
      ts = token.to_debug_str()
      raise btl_parser_error(f'Cannot transition from state "{context.state.name}" to "None" for token "{ts}"')
    
    new_state = self._find_state(new_state_name)
    if new_state == context.state:
      return
    attrs = 'attrs' #new_state._make_log_attributes(c)
    max_length = self._max_state_name_length
    msg = f'parser: transition: #{context.state.name:>{max_length}} -> {new_state.name:<{max_length}}# {attrs}'
    self.log_d(msg)
    if context.state != None:
      context.state.leave_state(context)
    context.state = new_state
    context.state.enter_state(context)

  _parse_result = namedtuple('_parse_result', 'root_node, tokens')
  def parse(self, text, source = None):
    check.check_string(text)
    check.check_string(source, allow_none = True)
    
    self.log_d(f'parser: parse: text=\"{text}\"')

    context = btl_parser_context(self, self._log_tag, text, source)
    self.do_start_commands(context)
    context.state.enter_state(context)
    
    tokens = btl_lexer_token_deque()
    first_time_set = set()
    last_position = btl_document_position(1, 1)
    for index, token in enumerate(self._lexer.lex_generator(text)):
      token_with_index = token.clone_replace_index(index)
      ts = token_with_index.to_debug_str()
      old_state_name = context.state.name
      first_time = old_state_name not in first_time_set
      first_time_set.add(old_state_name)
      self.log_d(f'parser: loop: token={ts} old_state_name={old_state_name} first_time={first_time}')
      context.position = last_position.advanced(' ')
      new_state_name = context.state.handle_token(context, token_with_index, first_time)
      self._change_state(context, new_state_name, token_with_index)
      tokens.append(token_with_index)
      if token_with_index.name != 't_eos':
        last_position = token_with_index.position

    if context.state != self.end_state:
      raise btl_parser_error(f'The end state is incorrectly "{context.state.name}" instead of "{self.end_state.name}"')

    self.do_end_commands(context)
    
    root_node = context.node_creator.remove_root_node()
    if len(context.node_creator) != 0:
      node_names = context.node_creator.node_names()
      orphaned_str = ' '.join(node_names)
      nodes_str = str(context.node_creator)
      raise btl_parser_error(f'Orphaned nodes found in end state: {orphaned_str}\nnodes:\n{nodes_str}')
    return self._parse_result(root_node, tokens)

  def do_start_commands(self, context):
    raise btl_parser_error(f'{self.name}: unhandled do_start_commands')

  def do_end_commands(self, context):
    raise btl_parser_error(f'{self.name}: unhandled do_end_commands')
  
check.register_class(btl_parser_base, name = 'btl_parser', include_seq = False)

#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod
from abc import ABCMeta

from ..system.log import log
from ..system.check import check
from ..property.cached_class_property import cached_class_property

from .btl_debug import btl_debug
from .btl_document_position import btl_document_position
from .btl_lexer_token_list import btl_lexer_token_list
from .btl_parser_context import btl_parser_context
from .btl_parser_desc import btl_parser_desc
from .btl_parser_error import btl_parser_error
from .btl_parser_node import btl_parser_node
from .btl_parser_node_creator import btl_parser_node_creator
from .btl_parser_options import btl_parser_options
from .btl_parser_result import btl_parser_result

class btl_parser_base(object):

  def __init__(self, log_tag, lexer, states):
    check.check_string(log_tag)
    check.check_btl_lexer(lexer)

    self._log_tag = log_tag
    self._lexer = lexer
    log.add_logging(self, tag = self._log_tag)
    self._states = states
    self._max_state_name_length = max([ len(state.name) for state in self._states.values() ])

  @classmethod
  @abstractmethod
  def desc_source(clazz):
    raise NotImplementedError(f'desc_source')

  @classmethod
  @abstractmethod
  def desc_text(clazz):
    raise NotImplementedError(f'desc_text')

  @abstractmethod
  def do_start_commands(self, context):
    raise NotImplementedError(f'do_start_commands')

  @abstractmethod
  def do_end_commands(self, context):
    raise NotImplementedError(f'do_end_commands')
  
  @cached_class_property
  def desc(clazz):
    return btl_parser_desc.parse_text(clazz.desc_text(), clazz.desc_source())
    
  @property
  def lexer(self):
    return self._lexer
    
  @property
  def start_state(self):
    return self._find_state(self.desc.header.start_state)

  @property
  def end_state(self):
    return self._find_state(self.desc.header.end_state)
  
  def _find_state(self, state_name):
    return self._states[state_name]
  
  def _change_state(self, context, new_state_name, token):
    if new_state_name == None:
      ts = token.to_debug_str()
      raise btl_parser_error(f'parser: cannot transition from state "{context.state.name}" to "None" for token "{ts}"')
    
    new_state = self._find_state(new_state_name)
    if new_state == context.state:
      return
    max_length = self._max_state_name_length
    msg = f'parser: transition: {context.state.name} -> {new_state.name} token={token.to_debug_str()}'
    self.log_i(msg)
    if context.state != None:
      context.state.leave_state(context)
    context.state = new_state
    context.state.enter_state(context)

  def parse(self, text, options = None):
    check.check_string(text)
    check.check_btl_parser_options(options, allow_none = True)

    options = options or btl_parser_options()
    context = btl_parser_context(self, self._log_tag, text, options)
    self.log_i(f'parser: parse: source=\"{context.source}\"')
    self.log_d(f'parser: parse: text=\"{text}\"')

    self.do_start_commands(context)
    context.state.enter_state(context)
    
    tokens = btl_lexer_token_list()
    last_position = btl_document_position(1, 1)
    for index, token in enumerate(self._lexer.lex_generator(text, options = options.lexer_options)):
      token.index = index
      ts = token.to_debug_str()
      old_state_name = context.state.name
      self.log_i(f'parser: loop: token={ts} old_state_name={old_state_name}')
      context.position = last_position.advanced(' ')
      new_state_name = context.state.handle_token(context, token)
      self._change_state(context, new_state_name, token)
      tokens.append(token)
      if token.name != 't_eos':
        last_position = token.position

    if context.state != self.end_state:
      raise btl_parser_error(f'The end state is incorrectly "{context.state.name}" instead of "{self.end_state.name}"')

    self.do_end_commands(context)
    
    root_node = context.node_creator.remove_root_node()
    if len(context.node_creator) != 0:
      node_names = context.node_creator.node_names()
      orphaned_str = ' '.join(node_names)
      nodes_str = str(context.node_creator)
      raise btl_parser_error(f'Orphaned nodes found in end state: {orphaned_str}\nnodes:\n{nodes_str}')
    return btl_parser_result(root_node, tokens)

check.register_class(btl_parser_base, name = 'btl_parser', include_seq = False)

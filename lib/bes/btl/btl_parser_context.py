#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.log import log
from ..system.check import check

from .btl_parser_node_creator import btl_parser_node_creator

class btl_parser_context(object):

  def __init__(self, parser, text, log_tag):
    check.check_btl_parser(parser)
    check.check_string(text)
    check.check_string(log_tag)
    
    self._parser = parser
    self._text = text
    self._node_creator = btl_parser_node_creator(log_tag)
    self._state = parser.start_state

  @property
  def node_creator(self):
    return self._node_creator

  @property
  def state(self):
    return self._state

  @state.setter
  def state(self, state):
    self._state = state

  def make_error_text(self, token):
    check.check_btl_lexer_token(token)

    lines = self._text.splitlines()
    top = lines[0:token.position.line]
    bottom = lines[token.position.line:]
    indent = ' ' * (token.position.column - 1)
    marker = f'{indent}^'
    error_lines = top + [ marker ] + bottom
    return os.linesep.join(error_lines)
    
check.register_class(btl_parser_context, include_seq = False)

#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.log import log
from ..system.check import check

from .btl_parser_node_creator import btl_parser_node_creator

class btl_parser_context(object):

  def __init__(self, parser, log_tag):
    check.check_btl_parser(parser)
    check.check_string(log_tag)
    
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
  
check.register_class(btl_parser_context, include_seq = False)

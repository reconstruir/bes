#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os

from ..system.log import log
from ..system.check import check

from .btl_parser_node_creator import btl_parser_node_creator
from .btl_document_position import btl_document_position

class btl_parser_context(object):

  def __init__(self, parser, log_tag, text, source):
    check.check_btl_parser(parser)
    check.check_string(log_tag)
    check.check_string(text)
    check.check_string(source, allow_none = True)
    
    self._position = None
    self._parser = parser
    self._text = text
    self._source = source or '<unknown>'
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

  @property
  def text(self):
    return self._text

  @property
  def source(self):
    return self._source

  @property
  def position(self):
    return self._position

  @position.setter
  def position(self, position):
    self._position = check.check_btl_document_position(position)
  
check.register_class(btl_parser_context, include_seq = False)

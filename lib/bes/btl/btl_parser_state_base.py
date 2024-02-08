#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.log import log
from ..system.check import check

from .btl_parser_error import btl_parser_error
from .btl_parser_node import btl_parser_node

class btl_parser_state_base(object):
  
  def __init__(self, parser, name, log_tag):
    check.check_string(name)
    check.check_string(log_tag)
    
    self.name = name
    log.add_logging(self, tag = log_tag)
    self._parser = parser

  @property
  def node_creator(self):
    return self._parser.node_creator

  @property
  def parser(self):
    return self._parser
    
  def handle_token(self, token):
    ts = token.to_debug_str()
    raise btl_parser_node(f'{self.name}: unhandled token: {ts}')

  def log_handle_token(self, token):
    ts = token.to_debug_str()
    self.log_d(f'{self.name}: handle_token: token={ts}')

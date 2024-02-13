#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.log import log
from ..system.check import check

from .btl_parser_error import btl_parser_error

class btl_parser_state_base(object):
  
  def __init__(self, parser, name, log_tag):
    check.check_string(name)
    check.check_string(log_tag)
    
    self.name = name
    log.add_logging(self, tag = log_tag)
    self._parser = parser

  @property
  def parser(self):
    return self._parser
  
  def handle_token(self, context, token):
    ts = token.to_debug_str()
    raise btl_parser_error(f'{self.name}: unhandled token: {ts}')

  def enter_state(self, context):
    raise btl_parser_error(f'{self.name}: unhandled enter_state')

  def leave_state(self, context):
    raise btl_parser_error(f'{self.name}: unhandled leave_state')
  
  def log_handle_token(self, token):
    ts = token.to_debug_str()
    self.log_d(f'{self.name}: handle_token: token={ts}')

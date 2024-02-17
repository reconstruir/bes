#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from ..system.check import check
from ..common.type_checked_list import type_checked_list

from .btl_parser_desc_state_transition import btl_parser_desc_state_transition

class btl_parser_desc_state_transition_list(type_checked_list):

  __value_type__ = btl_parser_desc_state_transition
  
  def __init__(self, values = None):
    super().__init__(values = values)

  def to_dict_list(self):
    result = []
    for transition in self:
      transition_dict = transition.to_dict()
      result.append(transition_dict)
    return result
    
  @classmethod
  def parse_node(clazz, n, source = '<unknown>'):
    check.check_node(n, allow_none = True)
    check.check_string(source)

    result = btl_parser_desc_state_transition_list()
    if not n:
      return result
    for child in n.children:
      next_desc_state_transition = btl_parser_desc_state_transition.parse_node(child, source)
      result.append(next_desc_state_transition)
    return result

  def generate_code(self, buf, errors):
    check.check_btl_code_gen_buffer(buf)
    errors = check.check_btl_lexer_desc_error_list(errors)

    for index, transition in enumerate(self):
      transition.generate_code(buf, errors, index, len(self))
  
btl_parser_desc_state_transition_list.register_check_class()

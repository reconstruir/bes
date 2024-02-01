#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from ..system.check import check
from ..common.type_checked_list import type_checked_list

from .btl_lexer_desc_state_transition import btl_lexer_desc_state_transition
from .btl_parsing import btl_parsing

class btl_lexer_desc_state_transition_list(type_checked_list):

  __value_type__ = btl_lexer_desc_state_transition
  
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
    check.check_node(n)
    check.check_string(source)

    result = btl_lexer_desc_state_transition_list()
    for child in n.children:
      next_desc_state_transition = btl_lexer_desc_state_transition.parse_node(child, source)
      result.append(next_desc_state_transition)
    return result

  def generate_code(self, buf, char_map):
    check.check_btl_code_gen_buffer(buf)
    check.check_btl_lexer_desc_char_map(char_map)

    for index, transition in enumerate(self):
      transition.generate_code(buf, char_map, index, len(self))
  
btl_lexer_desc_state_transition_list.register_check_class()

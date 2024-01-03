#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from ..system.check import check
from ..common.type_checked_list import type_checked_list

from .btl_desc_state import btl_desc_state
from .btl_parsing import btl_parsing

class btl_desc_state_list(type_checked_list):

  __value_type__ = btl_desc_state
  
  def __init__(self, values = None):
    super().__init__(values = values)

  def to_dict_list(self):
    result = []
    for state in self:
      state_dict = state.to_dict()
      result.append(state_dict)
    return result

  @classmethod
  def parse_node(clazz, n, end_state, source = '<unknown>'):
    check.check_node(n)
    check.check_string(source)
    check.check_string(end_state)

    result = btl_desc_state_list()
    for child in n.children:
      next_desc_state = btl_desc_state.parse_node(child, end_state, source = source)
      result.append(next_desc_state)
    return result

  def generate_code(self, buf, char_map):
    check.check_btl_code_gen_buffer(buf)
    check.check_btl_desc_char_map(char_map)

    for state in self:
      state.generate_code(buf, char_map)
  
btl_desc_state_list.register_check_class()  

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

  @classmethod
  def parse_node(clazz, n, source = '<unknown>'):
    check.check_node(n)
    check.check_string(source)

    result = btl_desc_state_list()
    for child in n.children:
      next_desc_state = btl_desc_state.parse_node(child, source)
      result.append(next_desc_state)
    return result
    
check.register_class(btl_desc_state_list, include_seq = False)

#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from ..system.check import check
from ..common.type_checked_list import type_checked_list

from .btl_desc_transition_command import btl_desc_transition_command
from .btl_parsing import btl_parsing

class btl_desc_transition_command_list(type_checked_list):

  __value_type__ = btl_desc_transition_command
  
  def __init__(self, values = None):
    super().__init__(values = values)

  @classmethod
  def parse_node(clazz, n, source = '<unknown>'):
    check.check_node(n)
    check.check_string(source)

    result = btl_desc_transition_command_list()
    for child in n.children:
      next_desc_error = btl_desc_transition_command.parse_node(child, source)
      result.append(next_desc_error)
    return result
    
check.register_class(btl_desc_transition_command_list, include_seq = False)

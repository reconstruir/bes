#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from ..system.check import check
from ..common.type_checked_list import type_checked_list

from .btl_desc_token import btl_desc_token
from .btl_parsing import btl_parsing

class btl_desc_token_list(type_checked_list):

  __value_type__ = btl_desc_token
  
  def __init__(self, values = None):
    super().__init__(values = values)

  def to_dict_list(self):
    result = []
    for token in self:
      token_dict = token.to_dict()
      result.append(token_dict)
    return result
    
  @classmethod
  def parse_node(clazz, n, source = '<unknown>'):
    check.check_node(n)
    check.check_string(source)

    result = btl_desc_token_list()
    for child in n.children:
      next_desc_error = btl_desc_token.parse_node(child, source)
      result.append(next_desc_error)
    return result

  def generate_code(self, buf):
    check.check_btl_code_gen_buffer(buf)

    for token in self:
      token.generate_code(buf)
    
btl_desc_token_list.register_check_class()

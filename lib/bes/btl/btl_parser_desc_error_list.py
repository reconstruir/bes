#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from ..system.check import check
from ..common.type_checked_list import type_checked_list

from .btl_parser_desc_error import btl_parser_desc_error

class btl_parser_desc_error_list(type_checked_list):

  __value_type__ = btl_parser_desc_error
  
  def __init__(self, values = None):
    super().__init__(values = values)

  def to_dict_list(self):
    result = []
    for error in self:
      error_dict = error.to_dict()
      result.append(error_dict)
    return result
    
  @classmethod
  def parse_node(clazz, n, source = '<unknown>'):
    check.check_node(n, allow_none = True)
    check.check_string(source)

    result = btl_parser_desc_error_list()
    if not n:
      return result
    for child in n.children:
      next_desc_error = btl_parser_desc_error.parse_node(child, source)
      result.append(next_desc_error)
    return result

  def find_error(self, name):
    for error in self:
      if error.name == name:
        return error
    return None

  def generate_code(self, buf):
    check.check_btl_code_gen_buffer(buf)

    for error in self:
      error.generate_code(buf)
  
btl_parser_desc_error_list.register_check_class()

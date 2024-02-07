#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from ..system.check import check
from ..common.type_checked_list import type_checked_list

from .btl_lexer_desc_error_list import btl_lexer_desc_error_list

class btl_desc_command_list(type_checked_list):

  def __init__(self, values = None):
    super().__init__(values = values)

  def to_dict_list(self):
    result = []
    for command in self:
      command_dict = command.to_dict()
      result.append(command_dict)
    return result
    
  @classmethod
  def parse_node(clazz, n, source = '<unknown>'):
    check.check_node(n, allow_none = True)
    check.check_string(source)

    result = clazz()
    if not n:
      return result
    for child in n.children:
      next_desc_command = clazz.__value_type__.parse_node(child, source)
      result.append(next_desc_command)
    return result

  def generate_code(self, buf, errors):
    check.check_btl_code_gen_buffer(buf)
    errors = check.check_btl_lexer_desc_error_list(errors)

    for command in self:
      command.generate_code(buf, errors)

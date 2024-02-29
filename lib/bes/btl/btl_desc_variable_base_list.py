#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from ..system.check import check
from ..common.type_checked_list import type_checked_list
from ..property.cached_property import cached_property
from ..common.variable_manager import variable_manager

from .btl_lexer_desc_error_list import btl_lexer_desc_error_list

class btl_desc_variable_base_list(type_checked_list):

  def __init__(self, values = None):
    super().__init__(values = values)

  def to_variable_manager(self):
    vm = variable_manager(add_system_variables = False)
    for var in self:
      vm.add_variable(var.name, var.default_value)
    return vm
  
  def to_dict_list(self):
    result = []
    for var in self:
      var_dict = var.to_dict()
      result.append(var_dict)
    return result
    
  @classmethod
  def parse_node(clazz, n, source = '<unknown>'):
    check.check_node(n, allow_none = True)
    check.check_string(source)

    result = clazz()
    if not n:
      return result
    for child in n.children:
      next_desc_var = clazz.__value_type__.parse_node(child, source)
      result.append(next_desc_var)
    return result

  def generate_code(self, buf, errors):
    check.check_btl_code_gen_buffer(buf)
    errors = check.check_btl_lexer_desc_error_list(errors)

    for var in self:
      var.generate_code(buf, errors)

  def to_dict(self):
    result = {}
    for var in self:
      result[var.name] = var.default_value
    return result

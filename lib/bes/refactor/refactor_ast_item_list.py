#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check
from bes.common.type_checked_list import type_checked_list

from .refactor_ast_item import refactor_ast_item

class refactor_ast_item_list(type_checked_list):

  __value_type__ = refactor_ast_item
  
  def __init__(self, values = None):
    super(refactor_ast_item_list, self).__init__(values = values)
  
check.register_class(refactor_ast_item_list, include_seq = False)

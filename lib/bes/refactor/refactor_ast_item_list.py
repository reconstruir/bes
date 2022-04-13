#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.algorithm import algorithm
from ..system.check import check
from bes.common.type_checked_list import type_checked_list

from .refactor_ast_item import refactor_ast_item

class refactor_ast_item_list(type_checked_list):

  __value_type__ = refactor_ast_item
  
  def __init__(self, values = None):
    super(refactor_ast_item_list, self).__init__(values = values)

  def make_file_map(self):
    result = {}
    for item in self:
      if not item.filename in result:
        result[item.filename] = []
      result[item.filename].append(item)
    return result

  def files(self):
    return algorithm.unique([ item.filename for item in self ])
  
check.register_class(refactor_ast_item_list, include_seq = False)

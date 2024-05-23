#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.system.check import check
from bes.common.type_checked_list import type_checked_list

from .bf_temp_item import bf_temp_item

class bf_temp_item_list(type_checked_list):

  __value_type__ = bf_temp_item
  
  def __init__(self, values = None):
    super().__init__(values = values)

  def write(clazz, root_dir):
    check.check_string(root_dir)
    
    for item in self:
      item.write(root_dir)
    
check.register_class(bf_temp_item_list, include_seq = False)

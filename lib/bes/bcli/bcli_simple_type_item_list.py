#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.common.type_checked_list import type_checked_list

from .bcli_simple_type_item import bcli_simple_type_item

class bcli_simple_type_item_list(type_checked_list):

  __value_type__ = bcli_simple_type_item
  
  def __init__(self, values = None):
    super().__init__(values = values)

check.register_class(bcli_simple_type_item_list, include_seq = False)
    

#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.common.type_checked_list import type_checked_list

from .bcli_type_i import bcli_type_i

class bcli_type_list(type_checked_list):

  __value_type__ = bcli_type_i
  
  def __init__(self, values = None):
    super().__init__(values = values)

check.register_class(bcli_type_list, include_seq = False)
    

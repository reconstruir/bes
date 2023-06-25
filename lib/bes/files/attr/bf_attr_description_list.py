#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.common.type_checked_list import type_checked_list

from .bf_attr_description import bf_attr_description

class bf_attr_description_list(type_checked_list):

  __value_type__ = bf_attr_description
  
  def __init__(self, values = None):
    super().__init__(values = values)

check.register_class(bf_attr_description_list, include_seq = False, cast_func = bf_attr_description_list.check_cast_func)

#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.common.type_checked_list import type_checked_list

from .bfile_attr_value import bfile_attr_value

class bfile_attr_value_list(type_checked_list):

  __value_type__ = bfile_attr_value
  
  def __init__(self, values = None):
    super().__init__(values = values)

check.register_class(bfile_attr_value_list, include_seq = False, cast_func = bfile_attr_value_list.check_cast_func)

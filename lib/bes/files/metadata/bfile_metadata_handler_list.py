#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.common.type_checked_list import type_checked_list

from .bfile_metadata_handler import bfile_metadata_handler

class bfile_metadata_handler_list(type_checked_list):

  __value_type__ = bfile_metadata_handler
  
  def __init__(self, values = None):
    super().__init__(values = values)

check.register_class(bfile_metadata_handler_list, include_seq = False, cast_func = bfile_metadata_handler_list.check_cast_func)

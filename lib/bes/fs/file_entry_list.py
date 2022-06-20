#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.check import check
from ..common.type_checked_list import type_checked_list

from .file_entry import file_entry

class file_entry_list(type_checked_list):

  __value_type__ = file_entry
  
  def __init__(self, values = None):
    super(file_entry_list, self).__init__(values = values)
  
check.register_class(file_entry_list, include_seq = False)

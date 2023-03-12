#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.check import check
from ..common.type_checked_list import type_checked_list

from .bfile_entry import bfile_entry

class bfile_entry_list(type_checked_list):

  __value_type__ = bfile_entry
  
  def __init__(self, values = None):
    super().__init__(values = values)

  def filenames(self):
    return [ entry.filename for entry in self ]

bfile_entry_list.register_check_class()

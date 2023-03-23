#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
from os import path

from ..system.check import check
from ..common.type_checked_list import type_checked_list

from .bfile_check import bfile_check
from .bfile_entry import bfile_entry
from .bfile_filename import bfile_filename

class bfile_entry_list(type_checked_list):

  __value_type__ = bfile_entry
  
  def __init__(self, values = None):
    super().__init__(values = values)

  def filenames(self):
    return [ entry.filename for entry in self ]

  def as_relative_list(self, head):
    check.check_string(head)

    result = bfile_entry_list()
    for entry in self:
      relative_filename = bfile_filename.remove_head(entry.filename, head)
      new_entry = bfile_entry(relative_filename, root_dir = entry.root_dir)
      result.append(new_entry)
    return result

  @classmethod
  def listdir(clazz, where):
    where = bfile_check.check_dir(where)
    
    files = sorted(os.listdir(where))
    files_abs = [ path.join(where, f) for f in files ]
    return bfile_entry_list([ bfile_entry(f, root_dir = where) for f in files_abs ])

bfile_entry_list.register_check_class()

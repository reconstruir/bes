#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
from os import path

from ..compat.cmp import cmp
from ..system.check import check
from ..common.type_checked_list import type_checked_list

from .bf_check import bf_check
from .bf_entry import bf_entry
from .bf_entry_sort_criteria import bf_entry_sort_criteria
from .bf_filename import bf_filename

class bf_entry_list(type_checked_list):

  __value_type__ = bf_entry
  
  def __init__(self, values = None):
    super().__init__(values = values)

  def filenames(self, sort = False):
    result = [ entry.filename for entry in self ]
    if sort:
      result.sort()
    return result

  def relative_filenames(self, sort = False):
    result = [ entry.relative_filename for entry in self ]
    if sort:
      result.sort()
    return result
  
  def basenames(self, sort = False):
    result = [ entry.basename for entry in self ]
    if sort:
      result.sort()
    return result

  def as_relative_list(self, head):
    check.check_string(head)

    result = bf_entry_list()
    for entry in self:
      relative_filename = bf_filename.remove_head(entry.filename, head)
      new_entry = bf_entry(relative_filename, root_dir = entry.root_dir)
      result.append(new_entry)
    return result

  @classmethod
  def listdir(clazz, where):
    where = bf_check.check_dir(where)
    
    files = sorted(os.listdir(where))
    files_abs = [ path.join(where, f) for f in files ]
    return bf_entry_list([ bf_entry(f, root_dir = where) for f in files_abs ])

  def sort_bt_criteria(self, sort_criteria, reverse = False):
    sort_criteria = check.check_bf_entry_sort_criteria(sort_criteria)

    self.sort(key = lambda entry: entry._compare_criteria(sort_criteria), reverse = reverse)

  def sorted_by_criteria(self, sort_criteria, reverse = False):
    return self.sorted_(key = lambda entry: entry._compare_criteria(sort_criteria), reverse = reverse)
    
bf_entry_list.register_check_class()

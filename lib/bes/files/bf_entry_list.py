#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
from os import path

from ..compat.cmp import cmp
from ..system.check import check
from ..common.type_checked_list import type_checked_list

from .bf_check import bf_check
from .bf_entry import bf_entry
from .bf_entry_sort_type import bf_entry_sort_type
from .bf_filename import bf_filename

class bf_entry_list(type_checked_list):

  __value_type__ = bf_entry
  
  def __init__(self, values = None):
    super().__init__(values = values)

  def filenames(self):
    return [ entry.filename for entry in self ]

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

  def compare(self, other, sort_type):
    check.check_bf_entry(other)
    sort_type = check.check_bf_entry_sort_type(sort_type)

    self_criteria = self._compare_criteria(sort_type)
    other_criteria = other._compare_criteria(sort_type)
    return cmp(self_criteria, other_criteria)

  def _compare_criteria(self, sort_type):
    sort_type = check.check_bf_entry_sort_type(sort_type)

    if sort_type == bf_entry_sort_type.BASENAME:
      return ( self.basename, )
    elif sort_type == bf_entry_sort_type.BASENAME_LOWERCASE:
      return ( self.basename_lowercase, )
    elif sort_type == bf_entry_sort_type.DIRNAME:
      return ( self.dirname, self.basename )
    elif sort_type == bf_entry_sort_type.DIRNAME_LOWERCASE:
      return ( self.dirname_lowercase, self.basename_lowercase )
    elif sort_type == bf_entry_sort_type.FILENAME:
      return ( self.filename, )
    elif sort_type == bf_entry_sort_type.FILENAME_LOWERCASE:
      return ( self.filename_lowercase, )
    elif sort_type == bf_entry_sort_type.MODIFICATION_DATE:
      return ( self.modification_date, self.filename_lowercase )
    elif sort_type == bf_entry_sort_type.SIZE:
      return ( self.size, self.filename_lowercase )
    else:
      assert False

  def sort_caca(self, sort_type, reverse = False):
    sort_type = check.check_bf_entry_sort_type(sort_type)

    self.sort(key = lambda entry: entry._compare_criteria(sort_type), reverse = reverse)

bf_entry_list.register_check_class()

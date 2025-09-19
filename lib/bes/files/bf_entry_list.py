#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
from os import path

from ..compat.cmp import cmp
from ..system.check import check
from ..common.type_checked_list import type_checked_list
from ..common.json_util import json_util
from ..common.dict_util import dict_util

from .bf_check import bf_check
from .bf_entry import bf_entry
from .bf_entry_sort_criteria import bf_entry_sort_criteria
from .bf_filename import bf_filename
from .bf_path import bf_path

class bf_entry_list(type_checked_list):

  __value_type__ = bf_entry
  
  def __init__(self, values = None):
    super().__init__(values = values)

  def to_dict_list(self):
    return [ entry.to_dict() for entry in self ]

  def to_json(self, replacements = None):
    dl = self.to_dict_list()
    if replacements:
      for d in dl:
        dict_util.replace_values(d, replacements)
    return json_util.to_json(dl)
  
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

  def absolute_filenames(self, sort = False):
    result = [ entry.absolute_filename for entry in self ]
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

    filenames = os.listdir(where)
    sorted_filenames = sorted(filenames)
    return bf_entry_list([ bf_entry(f, root_dir = where) for f in sorted_filenames ])

  def sort_bt_criteria(self, sort_criteria, reverse = False):
    sort_criteria = check.check_bf_entry_sort_criteria(sort_criteria)

    self.sort(key = lambda entry: entry._compare_criteria(sort_criteria), reverse = reverse)

  def sorted_by_criteria(self, sort_criteria, reverse = False):
    return self.sorted_(key = lambda entry: entry._compare_criteria(sort_criteria), reverse = reverse)

  def unreadable_files(self):
    return bf_entry_list([ entry for entry in self if not entry.is_readable ])

  def absolute_common_ancestor(self):
    return bf_path.common_ancestor(self.absolute_files())
  
bf_entry_list.register_check_class()

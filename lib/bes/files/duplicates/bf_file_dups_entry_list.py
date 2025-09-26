#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check

from ..bf_entry_list import bf_entry_list
from ..bf_entry_sort_criteria import bf_entry_sort_criteria

from .bf_file_dups_entry import bf_file_dups_entry

class bf_file_dups_entry_list(bf_entry_list):

  __value_type__ = bf_file_dups_entry
  
  def __init__(self, values = None):
    super().__init__(values = values)

  def checksum_map(self, hasher, algorithm, ignore_missing_files = True):
    result = {}
    for entry in self:
      try:
        checksum = hasher.checksum_sha(entry, algorithm, None, None)
        if not checksum in result:
          result[checksum] = bf_entry_list()
        result[checksum].append(entry)
      except FileNotFoundError as ex:
        if not ignore_missing_files:
          raise
    for _, entries in result.items():
      entries.sort_by_criteria(bf_entry_sort_criteria.FILENAME)
    return result

  def short_checksum_map(self, hasher, algorithm, ignore_missing_files = True):
    result = {}
    for entry in self:
      try:
        checksum = hasher.short_checksum_sha(entry, algorithm)
        if not checksum in result:
          result[checksum] = bf_entry_list()
        result[checksum].append(entry)
      except FileNotFoundError as ex:
        if not ignore_missing_files:
          raise
    for _, entries in result.items():
      entries.sort_by_criteria(bf_entry_sort_criteria.FILENAME)
    return result
    
check.register_class(bf_file_dups_entry_list, include_seq = False)

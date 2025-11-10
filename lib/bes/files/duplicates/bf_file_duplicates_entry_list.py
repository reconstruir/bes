#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.common.json_util import json_util

from ..bf_entry_list import bf_entry_list
from ..bf_entry_sort_criteria import bf_entry_sort_criteria

from .bf_file_duplicates_entry import bf_file_duplicates_entry

class bf_file_duplicates_entry_list(bf_entry_list):

  __value_type__ = bf_file_duplicates_entry
  
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

  def checksum_map_as_json(self, hasher, algorithm, ignore_missing_files = True,
                           replacements = None, xp_filenames = False):
    m = self.checksum_map(hasher, algorithm, ignore_missing_files = ignore_missing_files)
    return self._map_as_json(m, replacements, xp_filenames)
  
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

  def short_checksum_map_as_json(self, hasher, algorithm, ignore_missing_files = True,
                                 replacements = None, xp_filenames = False):
    m = self.short_checksum_map(hasher, algorithm, ignore_missing_files = ignore_missing_files)
    return self._map_as_json(m, replacements, xp_filenames)
  
  def basename_map(self):
    result = {}
    for entry in self:
      if not entry.basename in result:
        result[entry.basename] = bf_entry_list()
      result[entry.basename].append(entry)
    for _, entries in result.items():
      entries.sort_by_criteria(bf_entry_sort_criteria.FILENAME)
    return result

  def basename_map_as_json(self, replacements = None, xp_filenames = False):
    return self._map_as_json(self.basename_map(), replacements, xp_filenames)
  
  def size_map(self):
    result = {}
    for entry in self:
      try:
        size = entry.size
      except FileNotFoundError as ex:
        size = None
      if size != None:
        if not entry.size in result:
          result[entry.size] = bf_entry_list()
        result[entry.size].append(entry)
    for _, entries in result.items():
      entries.sort_by_criteria(bf_entry_sort_criteria.FILENAME)
    return result

  def size_map_as_json(self, replacements = None, xp_filenames = False):
    return self._map_as_json(self.size_map(), replacements, xp_filenames)
  
  @classmethod
  def _map_as_json(clazz, m, replacements, xp_filenames):
    result = {}
    for size, entries in m.items():
      result[size] = entries.to_dict_list(replacements = replacements, xp_filenames = xp_filenames)
    return json_util.to_json(result, indent = 2, sort_keys = True)
  
  @classmethod
  def map_filter_out_non_duplicates(clazz, m):
    result = {}
    for key, entries in m.items():
      if len(entries) > 1:
        assert key not in result
        result[key] = entries
    return result
  
check.register_class(bf_file_duplicates_entry_list, include_seq = False)

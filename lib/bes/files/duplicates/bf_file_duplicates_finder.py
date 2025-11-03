#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import pprint

from collections import namedtuple
import os.path as path

from bes.system.check import check
from bes.system.log import logger

from ..bf_check import bf_check

from ..hashing.bf_hasher_i import bf_hasher_i
from ..resolve.bf_file_resolver import bf_file_resolver

from .bf_file_duplicates_entry_list import bf_file_duplicates_entry_list
from .bf_file_duplicates_finder_item import bf_file_duplicates_finder_item
from .bf_file_duplicates_finder_item_list import bf_file_duplicates_finder_item_list
from .bf_file_duplicates_finder_options import bf_file_duplicates_finder_options
from .bf_file_duplicates_finder_result import bf_file_duplicates_finder_result

class bf_file_duplicates_finder(object):
  'A class to find duplicate files'

  _log = logger('bf_file_duplicates')

  def __init__(self, hasher, options = None):
    check.check_bf_hasher(hasher)
    check.check_bf_file_duplicates_finder_options(options, allow_none = True)

    self._options = bf_file_duplicates_finder_options.clone_or_create(options)
    self._hasher = hasher

  def _resolve_files(self, where):
    resolver = bf_file_resolver(options = self._options.file_resolver_options)
    return resolver.resolve(where)

  def find_duplicates(self, where):
    where = bf_check.check_file_or_dir_seq(where)

    resolved_entries = self._resolve_files(where)
    size_map = resolved_entries.size_map()
    self._log.log_d(f'size_map={pprint.pformat(size_map)}')
    dup_size_map = bf_file_duplicates_entry_list.map_filter_out_non_duplicates(size_map)
    num_dup_size_map = len(dup_size_map)
    self._log.log_d(f'dup_size_map={pprint.pformat(dup_size_map)}')
    flat_size_dup_files = self._flat_duplicate_files(dup_size_map)
    num_flat_size = len(flat_size_dup_files)
    self._log.log_d(f'flat_size_dup_files={pprint.pformat(flat_size_dup_files)}')
    short_checksum_map = flat_size_dup_files.short_checksum_map(self._hasher,
                                                                'sha256',
                                                                ignore_missing_files = True)
    dup_short_checksum_map = bf_file_duplicates_entry_list.map_filter_out_non_duplicates(short_checksum_map)
    flat_short_checksum_dup_files = self._flat_duplicate_files(dup_short_checksum_map)
    checksum_map = flat_short_checksum_dup_files.checksum_map(self._hasher,
                                                              'sha256',
                                                              ignore_missing_files = True)
    dup_checksum_map = bf_file_duplicates_entry_list.map_filter_out_non_duplicates(checksum_map)
    duplicate_items = bf_file_duplicates_finder_item_list()
    for checksum, dup_entries in dup_checksum_map.items():
      entry = dup_entries.pop(0)
      if self._match_function(entry, self._options):
        item = bf_file_duplicates_finder_item(entry, dup_entries)
        duplicate_items.append(item)
    self._log.log_d(f'dup_checksum_map={pprint.pformat(dup_checksum_map)}')
    return bf_file_duplicates_finder_result(resolved_entries, duplicate_items)

  @classmethod
  def find_file_duplicates(clazz, filename, where, options = None):
    filename = bf_check.check_file(filename)
    check.check_string_seq(where)
    check.check_bf_file_duplicates_finder_options(options, allow_none = True)

    options = options or bf_file_duplicates_finder_options()
    setup = clazz.setup(where, options = options)
    return clazz.find_file_duplicates_with_setup(filename, setup)

  @classmethod
  def _flat_duplicate_files(clazz, dup_size_map):
    result = bf_file_duplicates_entry_list()
    for size, entries in dup_size_map.items():
      result.extend(entries)
    result.sort_by_criteria('FILENAME')
    return result

  @classmethod
  def _sort_criteria_by_prefer_prefixes(clazz, filename, prefer_prefixes):
    if not prefer_prefixes:
      return None
    for p in prefer_prefixes:
      if filename.startswith(p):
        return 0
    return 1

  @classmethod
  def _sort_criteria_by_sort_key(clazz, filename, sort_key):
    if not sort_key:
      return None
    result = sort_key(filename)
    assert result != None
    return result

  @classmethod
  def _match_function(clazz, entry, options):
    try:
      clazz._log.log_d(f'_match_function: filename={entry.filename} include_empty_files={options.include_empty_files} is_empty={entry.is_empty}')
      if not options.include_empty_files:
        if entry.is_empty:
          return False
#      if options.should_ignore_file(filename):
#        return False
      return True
    except FileNotFoundError as ex:
      return False
  
  @classmethod
  def _resolve_one_file(clazz, filename):
    return file_duplicates_item(path.dirname(filename), path.basename(filename), filename, 0, 0)
  
  @classmethod
  def _sort_filename_list_by_preference(clazz, filenames, prefer_prefixes, sort_key):
    def _sort_key(filename):
      criteria = []
      function_criteria = clazz._sort_criteria_by_sort_key(filename, sort_key)
      if function_criteria != None:
        criteria.append(function_criteria)
      prefixes_criteria = clazz._sort_criteria_by_prefer_prefixes(filename, prefer_prefixes)
      if prefixes_criteria != None:
        criteria.append(prefixes_criteria)
      criteria.append(filename)
      return tuple(criteria)
    return sorted(filenames, key = _sort_key)

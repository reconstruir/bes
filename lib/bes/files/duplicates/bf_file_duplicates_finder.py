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
from .bf_file_duplicates_error import bf_file_duplicates_error
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

  def find_duplicates(self, where = None, resolved_entries = None):
    if not where and not resolved_entries:
      raise bf_file_duplicates_error(f'One of "where" or "resolved_entries" should be given.')

    if where and resolved_entries:
      raise bf_file_duplicates_error(f'Only one of "where" or "resolved_entries" should be given.')

    if where:
      where = bf_check.check_file_or_dir_seq(where)
      resolved_entries = self.resolve_files(where)
    else:
      assert resolved_entries
      check.check_bf_file_duplicates_entry_list(resolved_entries)
      
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
      def _sort_key(entry_):
        return self._sort_sort_criteria(entry_, self._options)
      dup_entries = dup_entries.sorted_(key = _sort_key)
      entry = dup_entries.pop(0)
      if self._match_function(entry, self._options):
        item = bf_file_duplicates_finder_item(entry, dup_entries)
        duplicate_items.append(item)
    self._log.log_d(f'dup_checksum_map={pprint.pformat(dup_checksum_map)}')
    return bf_file_duplicates_finder_result(resolved_entries, duplicate_items)

  def find_duplicates_with_resolved_entries(self, resolved_entries):
    check.check_bf_file_duplicates_entry_list(resolved_entries)
    return self._do_find_duplicates(resolved_entries)
  
  def resolve_files(self, where):
    resolver = bf_file_resolver(options = self._options.file_resolver_options)
    return resolver.resolve(where)
  
  def find_duplicates_for_entry(self, entry, where):
    check.check_bf_entry(entry)
    where = bf_check.check_file_or_dir_seq(where)

    resolved_entries = self.resolve_files(where)
    entry_short_checksum = None
    entry_checksum = None

    duplicate_entries = bf_file_duplicates_entry_list()
    for next_resolved_entry in resolved_entries:
      if next_resolved_entry.size != entry.size:
        continue
      next_resolved_entry_short_checksum = self._hasher.short_checksum_sha(next_resolved_entry, 'sha256')
      if entry_short_checksum == None:
        entry_short_checksum = self._hasher.short_checksum_sha(entry, 'sha256')
      if next_resolved_entry_short_checksum != entry_short_checksum:
        continue
      if entry_checksum == None:
        entry_checksum = self._hasher.checksum_sha(entry, 'sha256', None, None)
      next_resolved_entry_checksum = self._hasher.checksum_sha(next_resolved_entry, 'sha256', None, None)
      if next_resolved_entry_checksum != entry_checksum:
        continue
      duplicate_entries.append(next_resolved_entry)
    duplicate_items = bf_file_duplicates_finder_item_list()
    item = bf_file_duplicates_finder_item(entry, duplicate_entries)
    duplicate_items.append(item)
    return bf_file_duplicates_finder_result(resolved_entries, duplicate_items)

  @classmethod
  def _flat_duplicate_files(clazz, dup_size_map):
    result = bf_file_duplicates_entry_list()
    for size, entries in dup_size_map.items():
      result.extend(entries)
    result.sort_by_criteria('FILENAME')
    return result

  @classmethod
  def _sort_sort_criteria_by_prefer_prefixes(clazz, entry, options):
    if not options.prefer_prefixes:
      return []
    result = []
    for next_prefix in options.prefer_prefixes:
      positive = entry.absolute_filename.startswith(next_prefix)
      result.append(int(not positive))
    return result

  @classmethod
  def _sort_sort_criteria_by_sort_key(clazz, entry, options):
    if not options.sort_key:
      return []
    sort_key_result = options.sort_key(entry)
    if not isinstance(sort_key_result, list):
      raise bf_file_duplicates_error(f'return type of sort_key "{options.sort_key}" should be list instead of "{type(sort_key_result)}"')
    return sort_key_result

  @classmethod
  def _sort_sort_criteria(clazz, entry, options):
    sort_key_criteria = clazz._sort_sort_criteria_by_sort_key(entry, options)
    prefer_prefixes_criteria = clazz._sort_sort_criteria_by_prefer_prefixes(entry, options)
    return tuple(prefer_prefixes_criteria + sort_key_criteria)
  
  @classmethod
  def _match_function(clazz, entry, options):
    try:
      clazz._log.log_d(f'_match_function: filename={entry.filename} include_empty_files={options.include_empty_files} is_empty={entry.is_empty}')
      if not options.include_empty_files:
        if entry.is_empty:
          return False
      return True
    except FileNotFoundError as ex:
      return False

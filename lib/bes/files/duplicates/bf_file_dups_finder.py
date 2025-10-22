#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import pprint

from collections import namedtuple
import os.path as path

from bes.system.check import check
from bes.system.log import logger

from ..bf_check import bf_check

from ..hashing.bf_hasher_i import bf_hasher_i
from ..resolve.bf_file_resolver import bf_file_resolver

from .bf_file_dups_entry_list import bf_file_dups_entry_list
from .bf_file_dups_finder_item import bf_file_dups_finder_item
from .bf_file_dups_finder_item_list import bf_file_dups_finder_item_list
from .bf_file_dups_finder_options import bf_file_dups_finder_options
from .bf_file_dups_finder_result import bf_file_dups_finder_result
from .bf_file_dups_finder_setup import bf_file_dups_finder_setup

class bf_file_dups_finder(object):
  'A class to find duplicate files'

  _log = logger('bf_file_dups')

  def __init__(self, hasher, options = None):
    check.check_bf_hasher(hasher)
    check.check_bf_file_dups_finder_options(options, allow_none = True)

    self._options = bf_file_dups_finder_options.clone_or_create(options)
    self._hasher = hasher

  def _resolve_files(self, where):
    resolver = bf_file_resolver(options = self._options.file_resolver_options)
    return resolver.resolve(where)

  def _do_find_dups(self, where):
    resolved_files = self._resolve_files(where)
  
#  _dup_item = namedtuple('_dup_item', 'filename, duplicates')
#  _find_duplicates_result = namedtuple('_find_duplicates_result', 'items, resolved_files')
  def find_duplicates(self, where):
    where = bf_check.check_file_or_dir_seq(where)

    resolved_entries = self._resolve_files(where)
    size_map = resolved_entries.size_map()
    self._log.log_d(f'size_map={pprint.pformat(size_map)}')
    dup_size_map = bf_file_dups_entry_list.map_filter_out_non_duplicates(size_map)
    num_dup_size_map = len(dup_size_map)
    self._log.log_d(f'dup_size_map={pprint.pformat(dup_size_map)}')
    flat_size_dup_files = self._flat_duplicate_files(dup_size_map)
    num_flat_size = len(flat_size_dup_files)
    self._log.log_d(f'flat_size_dup_files={pprint.pformat(flat_size_dup_files)}')
    short_checksum_map = flat_size_dup_files.short_checksum_map(self._hasher,
                                                                'sha256',
                                                                ignore_missing_files = True)
    dup_short_checksum_map = bf_file_dups_entry_list.map_filter_out_non_duplicates(short_checksum_map)
    flat_short_checksum_dup_files = self._flat_duplicate_files(dup_short_checksum_map)
    checksum_map = flat_short_checksum_dup_files.checksum_map(self._hasher,
                                                              'sha256',
                                                              ignore_missing_files = True)
    dup_checksum_map = bf_file_dups_entry_list.map_filter_out_non_duplicates(checksum_map)
    duplicate_items = bf_file_dups_finder_item_list()
    for checksum, dup_entries in dup_checksum_map.items():
      entry = dup_entries.pop(0)
      item = bf_file_dups_finder_item(entry, dup_entries)
      duplicate_items.append(item)
    self._log.log_d(f'dup_checksum_map={pprint.pformat(dup_checksum_map)}')
    return bf_file_dups_finder_result(resolved_entries, duplicate_items)

  @classmethod
  def find_duplicates_with_setup(clazz, setup):
    check.check_bf_file_dups_finder_setup(setup)

    clazz._log.log_d(f'find_duplicates_with_setup: setup={setup.to_json()}', multi_line = True)
    items = []
    i = 1
    checksum_map_items = sorted(setup.dup_checksum_map.items())
    num = len(checksum_map_items)
    for checksum, where in checksum_map_items:
      sorted_where = clazz._sort_filename_list_by_preference(where,
                                                             setup.options.prefer_prefixes,
                                                             setup.options.sort_key)
      #for x in where:
      #  clazz._log.log_d(f'fdws:        where: {x}')
      #for x in sorted_where:
      #  clazz._log.log_d(f'fdws: sorted_where: {x}')
      filename = sorted_where[0]
      duplicates = sorted_where[1:]
      item = clazz._dup_item(filename, duplicates)
      items.append(item)
      i = i + 1
    return clazz._find_duplicates_result(items, setup.resolved_files)
  
  def setup(self, where):
    check.check_string_seq(where)
    #check.check_bf_file_dups_finder_options(options, allow_none = True)

    resolved_files = self._resolve_files(where)
    return bf_file_dups_finder_setup(where, resolved_files, self._options)
    
  @classmethod
  def find_file_duplicates(clazz, filename, where, options = None):
    filename = bf_check.check_file(filename)
    check.check_string_seq(where)
    check.check_bf_file_dups_finder_options(options, allow_none = True)

    options = options or bf_file_dups_finder_options()
    setup = clazz.setup(where, options = options)
    return clazz.find_file_duplicates_with_setup(filename, setup)

  @classmethod
  def find_file_duplicates_with_setup(clazz, filename, setup):
    filename = bf_check.check_file(filename)
    check.check_bf_file_dups_finder_setup(setup)

    resolved_one_file = clazz._resolve_one_file(filename)
    new_resolved_files = setup.resolved_files
    new_resolved_files.append(resolved_one_file)
    new_setup = setup.clone(mutations = { 'resolved_files': new_resolved_files })
    dups_result = clazz.find_duplicates_with_setup(new_setup)
    return clazz._compute_file_duplicates(dups_result, filename)

  @classmethod
  def _compute_file_duplicates(clazz, dups_result, filename):
    result = []
    for item in dups_result.items:
      #clazz._log.log_d(f'item={item}')
      all_files = set([ item.filename ] + item.duplicates)
      #clazz._log.log_d(f'all_files={all_files}')
      if filename in all_files:
        all_files.remove(filename)
        result.extend(list(all_files))
    #clazz._log.log_d(f'result={result}')
    return sorted(result)
  
  @classmethod
  def _flat_duplicate_files(clazz, dup_size_map):
    result = bf_file_dups_entry_list()
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
  def _match_function(clazz, filename, options):
    try:
      if not options.include_empty_files:
        if file_util.is_empty(filename):
          return False
      if options.should_ignore_file(filename):
        return False
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

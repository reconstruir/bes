#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
import os.path as path

from bes.fs.file_check import file_check
from bes.fs.file_resolver import file_resolver
from bes.fs.file_resolver_item import file_resolver_item
from bes.fs.file_resolver_item_list import file_resolver_item_list
from bes.fs.file_resolver_options import file_resolver_options
from bes.system.check import check
from bes.system.log import logger

from .file_attributes_metadata import file_attributes_metadata
from .file_check import file_check
from .file_duplicates_options import file_duplicates_options
from .file_duplicates_setup import file_duplicates_setup
from .file_util import file_util

class file_duplicates(object):
  'A class to find duplicate files'

  _log = logger('file_duplicates')

  _dup_item = namedtuple('_dup_item', 'filename, duplicates')
  _find_duplicates_result = namedtuple('_find_duplicates_result', 'items, resolved_files')
  @classmethod
  def find_duplicates(clazz, where, options = None):
    check.check_string_seq(where)
    check.check_file_duplicates_options(options, allow_none = True)

    options = options or file_duplicates_options()
    setup = clazz.setup(where, options = options)
    return clazz.find_duplicates_with_setup(setup)

  @classmethod
  def find_duplicates_with_setup(clazz, setup):
    check.check_file_duplicates_setup(setup)

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
  
  @classmethod
  def setup(clazz, where, options = None):
    check.check_string_seq(where)
    check.check_file_duplicates_options(options, allow_none = True)

    options = options or file_duplicates_options()
    resolved_files = clazz._resolve_files(where, options)
    options.blurber.blurb_verbose(f'resolved {len(resolved_files)} files')
    return file_duplicates_setup(where, resolved_files, options)
    
  @classmethod
  def find_file_duplicates(clazz, filename, where, options = None):
    filename = file_check.check_file(filename)
    check.check_string_seq(where)
    check.check_file_duplicates_options(options, allow_none = True)

    options = options or file_duplicates_options()
    setup = clazz.setup(where, options = options)
    return clazz.find_file_duplicates_with_setup(filename, setup)

  @classmethod
  def find_file_duplicates_with_setup(clazz, filename, setup):
    filename = file_check.check_file(filename)
    check.check_file_duplicates_setup(setup)

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
  def _flat_duplicate_files(clazz, dmap):
    result = []
    for size, files in sorted(dmap.items()):
      result.extend(files)
    return sorted(result)

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
  def _resolve_files(clazz, files, options):
    match_function = lambda filename: clazz._match_function(filename, options)
    resolver_options = file_resolver_options(recursive = options.recursive,
                                             match_basename = False,
                                             match_function = match_function)
    return file_resolver.resolve_files(files, options = resolver_options)

  @classmethod
  def _resolve_one_file(clazz, filename):
    return file_resolver_item(path.dirname(filename), path.basename(filename), filename, 0, 0)
  
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
  
  @classmethod
  def _small_checksum_map(clazz, files, num_bytes):
    result = {}
    for filename in files:
      small_checksum = file_util.checksum('sha256', filename, chunk_size = num_bytes, num_chunks = 1)
      if not small_checksum in result:
        result[small_checksum] = []
      result[small_checksum].append(filename)
    return result

  @classmethod
  def _duplicate_small_checksum_map(clazz, dmap):
    result = {}
    for small_checksum, files in sorted(dmap.items()):
      if len(files) > 1:
        assert small_checksum not in result
        result[small_checksum] = files
    return result

  @classmethod
  def _checksum_map(clazz, files):
    result = {}
    for filename in files:
      checksum = file_attributes_metadata.get_checksum_sha256(filename, fallback = True, cached = True)
      if not checksum in result:
        result[checksum] = []
      result[checksum].append(filename)
    return result

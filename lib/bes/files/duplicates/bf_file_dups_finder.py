#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
import os.path as path

from bes.system.check import check
from bes.system.log import logger

from ..bf_check import bf_check

from ..hashing.bf_hasher_i import bf_hasher_i
from ..resolve.bf_file_resolver import bf_file_resolver

from .bf_file_dups_finder_options import bf_file_dups_finder_options
from .bf_file_dups_finder_result import bf_file_dups_finder_result
from .bf_file_dups_finder_item import bf_file_dups_finder_item

class bf_file_dups_finder(object):
  'A class to find duplicate files'

  _log = logger('bf_file_dups_finder')

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
  
  _dup_item = namedtuple('_dup_item', 'filename, duplicates')
  _find_duplicates_result = namedtuple('_find_duplicates_result', 'items, resolved_files')
  @classmethod
  def find_duplicates(clazz, where, options = None):
    check.check_string_seq(where)
    check.check_bf_file_dups_finder_options(options, allow_none = True)

    options = options or bf_file_dups_finder_options()
    setup = clazz.setup(where, options = options)
    return clazz.find_duplicates_with_setup(setup)

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
  
  @classmethod
  def setup(clazz, where, options = None, blurber = None):
    check.check_string_seq(where)
    check.check_bf_file_dups_finder_options(options, allow_none = True)

    options = options or bf_file_dups_finder_options()
    resolved_files = clazz._resolve_files(where, options)
    if blurber:
      blurber.blurb_verbose(f'resolved {len(resolved_files)} files')
    return bf_file_dups_finder_setup(where, resolved_files, options)
    
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
  def x_resolve_files(clazz, files, options):
    match_function = lambda filename: clazz._match_function(filename, options)
    resolver_options = bf_file_dups_finder_options(recursive = options.recursive,
                                                  match_basename = False,
                                                  match_function = match_function)
    return file_resolver.resolve_files(files, options = resolver_options)

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

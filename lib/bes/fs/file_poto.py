#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
import os.path as path

from bes.system.check import check
from bes.system.log import logger
from bes.fs.file_resolver import file_resolver
from bes.fs.file_resolver_item_list import file_resolver_item_list
from bes.fs.file_resolver_options import file_resolver_options

from .file_poto_options import file_poto_options
from .file_check import file_check
from .file_util import file_util
from .file_attributes_metadata import file_attributes_metadata

class file_poto(object):
  'A class to find duplicate files'

  _log = logger('file_poto')

  _dup_item = namedtuple('_dup_item', 'filename, duplicates')
  _find_duplicates_result = namedtuple('_find_duplicates_result', 'items, resolved_files')
  @classmethod
  def find_duplicates(clazz, files, options = None):
    check.check_string_seq(files)
    check.check_file_poto_options(options, allow_none = True)

    options = options or file_poto_options()
    resolved_files = clazz._resolve_files(files, options.recursive)
    dmap = resolved_files.duplicate_size_map()
    flat_size_dup_files = clazz._flat_duplicate_files(dmap)
    small_checksum_map = clazz._small_checksum_map(flat_size_dup_files, options.small_checksum_size)
    dup_small_checksum_map = clazz._duplicate_small_checksum_map(small_checksum_map)
    flat_small_checksum_dup_files = clazz._flat_duplicate_files(dup_small_checksum_map)
    checksum_map = clazz._checksum_map(flat_small_checksum_dup_files)
    dup_checksum_map = clazz._duplicate_small_checksum_map(checksum_map)

    items = []
    for checksum, files in sorted(dup_checksum_map.items()):
      sorted_files = clazz._sort_filename_list_by_preference(files,
                                                             options.prefer_prefixes,
                                                             options.prefer_function)
      filename = sorted_files[0]
      duplicates = sorted_files[1:]
      item = clazz._dup_item(filename, duplicates)
      items.append(item)
    return clazz._find_duplicates_result(items, resolved_files)

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
  def _sort_criteria_by_prefer_function(clazz, filename, prefer_function):
    if not prefer_function:
      return None
    result = prefer_function(filename)
    assert result != None
    return result
  
  @classmethod
  def _resolve_files(clazz, files, recursive):
    resolver_options = file_resolver_options(recursive = recursive)
    return file_resolver.resolve_files(files, options = resolver_options)

  @classmethod
  def _sort_filename_list_by_preference(clazz, filenames, prefer_prefixes, prefer_function):
    def _sort_key(filename):
      criteria = []
      function_criteria = clazz._sort_criteria_by_prefer_function(filename, prefer_function)
      if function_criteria != None:
        criteria.append(function_criteria)
      prefixes_criteria = clazz._sort_criteria_by_prefer_prefixes(filename, prefer_prefixes)
      if prefixes_criteria != None:
        criteria.append(prefixes_criteria)
      criteria.append(filename)
      print(f'f={filename} c={criteria}')
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
      checksum = file_attributes_metadata.get_checksum_cached(filename, fallback = True)
      if not checksum in result:
        result[checksum] = []
      result[checksum].append(filename)
    return result
  
  @staticmethod
  def prefer_function(filename):
    
    result = {}
    for filename in files:
      checksum = file_attributes_metadata.get_checksum_cached(filename, fallback = True)
      if not checksum in result:
        result[checksum] = []
      result[checksum].append(filename)
    return result
  

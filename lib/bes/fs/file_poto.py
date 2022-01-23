#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
import os.path as path

from bes.common.algorithm import algorithm
from bes.common.object_util import object_util
from bes.common.string_util import string_util
from bes.system.check import check
from bes.system.log import logger
from bes.fs.file_resolver import file_resolver
from bes.fs.file_resolver_options import file_resolver_options

from .dir_operation_item import dir_operation_item
from .dir_operation_item_list import dir_operation_item_list
from .dir_operation_util import dir_operation_util
from .file_poto_options import file_poto_options
from .file_poto_type import file_poto_type
from .file_attributes_metadata import file_attributes_metadata
from .file_check import file_check
from .file_find import file_find
from .file_path import file_path
from .file_util import file_util
from .filename_list import filename_list

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
    flat_size_dups = clazz._flat_duplicate_files(dmap)
    small_checksum_map = clazz._small_checksum_map(flat_size_dups, 1024)
    dup_small_checksum_map = clazz._duplicate_small_checksum_map(small_checksum_map)
    items = []
    for small_checksum, files in sorted(dup_small_checksum_map.items()):
      filename = files[0]
      duplicates = files[1:]
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
  def _resolve_files(clazz, files, recursive):
    #sort_order = 'depth',
    #sort_reverse = True,
    resolver_options = file_resolver_options(recursive = recursive)
    return file_resolver.resolve_files(files, options = resolver_options)

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

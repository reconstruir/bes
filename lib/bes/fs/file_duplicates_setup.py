#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from ..common.check import check
from ..common.tuple_util import tuple_util
from ..property.cached_property import cached_property

from .file_attributes_metadata import file_attributes_metadata
from .file_resolver_item_list import file_resolver_item_list
from .file_util import file_util

class file_duplicates_setup(namedtuple('file_duplicates_setup', 'files, resolved_files, options')):

  def __new__(clazz, files, resolved_files, options):
    check.check_string_seq(files)
    check.check_file_resolver_item_list(resolved_files)
    check.check_file_duplicates_options(options)

    return clazz.__bases__[0].__new__(clazz, files, resolved_files, options)

  def clone(self, mutations = None):
    return tuple_util.clone(self, mutations = mutations)

  @cached_property
  def dup_checksum_map(self):
    dmap = self.resolved_files.duplicate_size_map()
    flat_size_dup_files = self._flat_duplicate_files(dmap)
    small_checksum_map = self._small_checksum_map(flat_size_dup_files,
                                                  self.options.small_checksum_size)
    dup_small_checksum_map = self._duplicate_small_checksum_map(small_checksum_map)
    flat_small_checksum_dup_files = self._flat_duplicate_files(dup_small_checksum_map)
    checksum_map = self._checksum_map(flat_small_checksum_dup_files)
    return self._duplicate_small_checksum_map(checksum_map)
  
  @classmethod
  def _flat_duplicate_files(clazz, dmap):
    result = []
    for size, files in sorted(dmap.items()):
      result.extend(files)
    return sorted(result)

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
  
check.register_class(file_duplicates_setup, include_seq = False)

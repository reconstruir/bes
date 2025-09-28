#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import dataclasses
import typing

from collections import namedtuple

from bes.bcli.bcli_type_i import bcli_type_i
from bes.system.check import check
from bes.property.cached_property import cached_property
from bes.data_classes.bdata_class_base import bdata_class_base

from .bf_file_dups_finder_options import bf_file_dups_finder_options
from .bf_file_dups_entry_list import bf_file_dups_entry_list

@dataclasses.dataclass(frozen = True)
class bf_file_dups_finder_setup(bdata_class_base):
  where: typing.List[str]
  resolved_entries: bf_file_dups_entry_list
  options: bf_file_dups_entry_list

  def to_dict(self):
    return {
      'where': self.where,
      'resolved_entries': self.resolved_entries.to_dict_list(),
      'options': self.options.to_dict(),
    }
  
#  def to_json_dict_hook(self, d):
#    d['resolved_entries'] = self.resolved_entries.to_dict_list()
#    d['options'] = self.options.to_dict()
#    return d

  @cached_property
  def dup_checksum_map(self):
    dmap = self.resolved_entries.duplicate_size_map()
    num_dmap = len(dmap)
    #self.options.blurber.blurb_verbose(f'found {num_dmap} duplicate sizes')
    flat_size_dup_files = self._flat_duplicate_files(dmap)
    num_flat_size = len(flat_size_dup_files)
    #self.options.blurber.blurb_verbose(f'found {num_flat_size} files to check')
    small_checksum_map = self._small_checksum_map(flat_size_dup_files,
                                                  self.options.small_checksum_size,
                                                  blurber = None)
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
  def _small_checksum_map(clazz, files, num_bytes, blurber = None):
    result = {}
    num = len(files)
    for i, filename in enumerate(files, start = 1):
      if blurber:
        blurber.blurb_verbose(f'checking {i} of {num}: {filename}')
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
      try:
        checksum = file_attributes_metadata.get_checksum_sha256(filename, fallback = True, cached = True)
        if not checksum in result:
          result[checksum] = []
        result[checksum].append(filename)
      except FileNotFoundError as ex:
        pass
      
    return result
  
check.register_class(bf_file_dups_finder_setup, include_seq = False)

class cli_bf_file_dups_finder_setup(bcli_type_i):

  @classmethod
  #@abstractmethod
  def name_str(clazz):
    return 'bf_file_dups_finder_setup'

  @classmethod
  #@abstractmethod
  def type_function(clazz):
    return bf_file_dups_finder_setup

  @classmethod
  #@abstractmethod
  def parse(clazz, text):
    assert False
    return text

  @classmethod
  #@abstractmethod
  def check(clazz, value, allow_none = False):
    return check.check_bf_file_dups_finder_setup(value, allow_none = allow_none)

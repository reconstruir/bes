#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.common.algorithm import algorithm
from bes.common.check import check
from bes.common.type_checked_list import type_checked_list
from bes.text.string_list import string_list

from .file_resolver_item import file_resolver_item
from .file_path import file_path

class file_resolver_item_list(type_checked_list):

  __value_type__ = file_resolver_item
  
  def __init__(self, values = None):
    super(file_resolver_item_list, self).__init__(values = values)

  def absolute_files(self, sort = False):
    result = [ item.filename_abs for item in self ]
    if sort:
      result = sorted(result)
    return string_list(result)

  def absolute_common_ancestor(self):
    return file_path.common_ancestor(self.absolute_files())
  
  def relative_files(self, sort = False):
    result = [ item.filename for item in self ]
    if sort:
      result = sorted(result)
    return string_list(result)

  def basenames(self, sort = False):
    result = [ path.basename(item.filename_abs) for item in self ]
    if sort:
      result = sorted(result)
    return string_list(result)
  
  def root_dirs(self):
    return set([ item.root_dir for item in self ])
  
  def output(self, label = None):
    label = label or ''
    for item in self:
      print(f'{label}{item.index}:{item.root_dir}:{item.filename}')

  def media_types(self):
    return set([ file_attributes_metadata.get_media_type_cached(f.filename_abs, fallback = True) for f in self ])

  def basename_map(self):
    result = {}
    for item in self:
      if not item.basename in result:
        result[item.basename] = file_resolver_item_list()
      result[item.basename].append(item)
    return result

  def filename_abs_map(self):
    result = {}
    for item in self:
      assert not item.filename_abs in result
      result[item.filename_abs] = item
    return result
  
  def duplicate_basename_map(self):
    result = {}
    for basename, items in self.basename_map().items():
      if len(items) > 1:
        assert basename not in result
        result[basename] = items.absolute_files(sort = True)
    return result

  def size_map(self):
    result = {}
    for item in self:
      if not item.size in result:
        result[item.size] = file_resolver_item_list()
      result[item.size].append(item)
    return result

  def duplicate_size_map(self):
    result = {}
    for size, items in self.size_map().items():
      if len(items) > 1:
        assert size not in result
        result[size] = items.absolute_files(sort = True)
    return result
  
check.register_class(file_resolver_item_list, include_seq = False)

#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.common.algorithm import algorithm
from bes.common.check import check
from bes.common.type_checked_list import type_checked_list

from .dir_operation_item import dir_operation_item
from .file_util import file_util

class dir_operation_item_list(type_checked_list):

  __value_type__ = dir_operation_item
  
  def __init__(self, values = None):
    super(dir_operation_item_list, self).__init__(values = values)

  def move_files(self, timestamp, count):
    result = []
    resolved_items = self.resolve_for_move(timestamp, count)
    for item in resolved_items:
      need_move = False
      if path.exists(item.dst_filename):
        need_move = file_util.files_are_the_same(item.src_filename,
                                                 item.dst_filename)
      else:
        need_move = True
      if need_move:
        file_util.rename(item.src_filename, item.dst_filename)
        result.append(item.dst_filename)
    return result
        
  @classmethod
  def _make_resolved_filename(clazz, filename, timestamp, count):
    basename = path.basename(filename)
    dirname = path.dirname(filename)
    return path.join(dirname, f'{timestamp}-{count}-{basename}')

  def resolve_for_move(self, timestamp, count):
    main_map = {}
    for item in self:
      if not item.dst_dirname in main_map:
        main_map[item.dst_dirname] = {}
      dir_map = main_map[item.dst_dirname]
      if item.dst_basename in dir_map:
        new_dst_filename = self._make_resolved_filename(item.dst_filename, timestamp, count)
        count += 1
        new_item = item.clone(mutations = { 'dst_filename': new_dst_filename })
      else:
        new_item = item
      dir_map[new_item.dst_basename] = new_item
    result = dir_operation_item_list()
    for _, dir_map in main_map.items():
      for __, item in dir_map.items():
        result.append(item)
    result.sort(key = lambda item: item.dst_filename)
    return result
        
check.register_class(dir_operation_item_list, include_seq = False)

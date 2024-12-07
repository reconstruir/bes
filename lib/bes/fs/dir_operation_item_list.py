#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.common.algorithm import algorithm
from ..system.check import check
from bes.common.type_checked_list import type_checked_list
from bes.common.time_util import time_util

from .dir_operation_item import dir_operation_item
from .file_util import file_util
from .filename_util import filename_util

class dir_operation_item_list(type_checked_list):

  __value_type__ = dir_operation_item
  
  def __init__(self, values = None):
    super().__init__(values = values)

  def move_files(self, timestamp, count, callback = None, touch = False):
    check.check_string(timestamp, allow_none = True)
    check.check_int(count, allow_none = True)
    check.check_callable(callback, allow_none = True)

    result = []
    resolved_items = self.resolve_for_move(timestamp, count)
    num = len(resolved_items)
    for i, item in enumerate(resolved_items, start = 1):
      need_move = False
      if path.exists(item.dst_filename):
        #assert file_util.files_are_the_same(item.src_filename,
        #                                    item.dst_filename)
        #print(f'checking {item.src_filename} vs {item.dst_filename}')
        need_move = file_util.files_are_the_same(item.src_filename,
                                                 item.dst_filename)
      else:
        need_move = True
      if need_move:
        file_util.rename(item.src_filename, item.dst_filename)
        if touch:
          file_util.touch(item.dst_filename)
        result.append(item.dst_filename)
      if callback:
        callback(item, i, num)
    return result

  def copy_files(self, timestamp, count, callback = None, touch_files = False):
    check.check_string(timestamp, allow_none = True)
    check.check_int(count, allow_none = True)
    check.check_callable(callback, allow_none = True)

    result = []
    resolved_items = self.resolve_for_move(timestamp, count)
    num = len(resolved_items)
    for i, item in enumerate(resolved_items, start = 1):
      need_copy = False
      if path.exists(item.dst_filename):
        assert file_util.files_are_the_same(item.src_filename,
                                            item.dst_filename)
        need_copy = file_util.files_are_the_same(item.src_filename,
                                                 item.dst_filename)
      else:
        need_copy = True
      if need_copy:
        file_util.copy(item.src_filename, item.dst_filename)
        if touch_files:
          file_util.touch(item.dst_filename)
        result.append(item.dst_filename)
      if callback:
        callback(item, i, num)
    return result
  
  @classmethod
  def _make_resolved_filename(clazz, filename, timestamp, count):
    basename = path.basename(filename)
    dirname = path.dirname(filename)
    basename_no_ext = filename_util.without_extension(basename)
    ext = filename_util.extension(basename)
    new_basename_no_ext = f'{basename_no_ext}-{timestamp}-{count}'
    new_basename = filename_util.add_extension(new_basename_no_ext, ext)
    return path.join(dirname, new_basename)

  def resolve_for_move(self, timestamp, count):
    check.check_string(timestamp, allow_none = True)
    check.check_int(count, allow_none = True)

    timestamp = timestamp or time_util.timestamp()
    count = count or 1
    
    main_map = {}
    for item in self:
      if not item.dst_dirname in main_map:
        main_map[item.dst_dirname] = {}
      dir_map = main_map[item.dst_dirname]
      if item.dst_basename in dir_map or (item.dst_exists() and not item.src_and_dst_are_the_same()):
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

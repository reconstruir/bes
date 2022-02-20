#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.common.algorithm import algorithm
from bes.common.check import check
from bes.common.type_checked_list import type_checked_list

from .dir_operation_item import dir_operation_item
from .file_path import file_path
from .file_check import file_check
from .file_util import file_util

class dir_operation_item_list(type_checked_list):

  __value_type__ = dir_operation_item
  
  def __init__(self, values = None):
    super(dir_operation_item_list, self).__init__(values = values)

  def move_files(self, timestamp, count):
    for item in self:
      #print(f'moving: {item}')
      if self._move_with_duplicate(item.src_filename,
                                   item.dst_filename,
                                   f'{timestamp}-{count}'):
        count += 1

  @classmethod
  def _move_with_duplicate(clazz, src, dst, prefix):
    src = file_check.check_file(src)
    check.check_string(prefix)

    if src == dst:
      return False
    
    if not path.exists(dst):
      file_util.rename(src, dst)
      return False

    if file_util.files_are_the_same(src, dst):
      return False
    
    basename = path.basename(dst)
    dirname = path.dirname(dst)
    dst_basename = f'{prefix}-{basename}'
    dst_filename = path.join(dirname, dst_basename)
    #assert False, f'FUCKYOU: {src} => {dst_filename}'
    file_util.rename(src, dst_filename)
    return True

check.register_class(dir_operation_item_list, include_seq = False)

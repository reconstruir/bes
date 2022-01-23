#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from collections import namedtuple

from bes.common.check import check
from bes.common.tuple_util import tuple_util
from bes.property.cached_property import cached_property

from .file_path import file_path
from .file_util import file_util
from .dir_operation_item_type import dir_operation_item_type

class dir_operation_item(namedtuple('dir_operation_item', 'src_filename, dst_filename, operation_type')):

  def __new__(clazz, src_filename, dst_filename, operation_type):
    check.check_string(src_filename)
    check.check_string(dst_filename)
    operation_type = check.check_dir_operation_item_type(operation_type)

    return clazz.__bases__[0].__new__(clazz, src_filename, dst_filename, operation_type)

  def clone(self, mutations = None):
    return tuple_util.clone(self, mutations = mutations)

  @cached_property
  def dst_basename(self):
    return file_path.part(self.dst_filename, -2)

  def execute_operation(self, prefix):
    if self.operation_type == dir_operation_item_type.MOVE:
      return file_util.move_with_duplicate(self.src_filename,
                                           self.dst_filename,
                                           prefix)
    elif self.operation_type == dir_operation_item_type.REMOVE:
      if path.exists(self.src_filename):
        file_util.remove(self.src_filename)
        return True
      return False
    else:
      assert False
  
check.register_class(dir_operation_item, include_seq = False)

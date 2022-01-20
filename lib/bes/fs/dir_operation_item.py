#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from collections import namedtuple

from bes.common.check import check
from bes.common.tuple_util import tuple_util
from bes.property.cached_property import cached_property

from .file_path import file_path

class dir_operation_item(namedtuple('dir_operation_item', 'src_filename, dst_filename')):

  def __new__(clazz, src_filename, dst_filename):
    check.check_string(src_filename)
    check.check_string(dst_filename)

    return clazz.__bases__[0].__new__(clazz, src_filename, dst_filename)

  def clone(self, mutations = None):
    return tuple_util.clone(self, mutations = mutations)

  @cached_property
  def dst_basename(self):
    return file_path.part(self.dst_filename, -2)
  
check.register_class(dir_operation_item, include_seq = False)

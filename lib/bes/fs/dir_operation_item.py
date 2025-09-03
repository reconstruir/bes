#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from collections import namedtuple

from ..system.check import check
from bes.common.tuple_util import tuple_util
from bes.property.cached_property import cached_property
from bes.common.time_util import time_util

from bes.files.bf_path import bf_path
from .file_util import file_util

class dir_operation_item(namedtuple('dir_operation_item', 'src_filename, dst_filename')):

  def __new__(clazz, src_filename, dst_filename):
    check.check_string(src_filename)
    check.check_string(dst_filename)

    return clazz.__bases__[0].__new__(clazz, src_filename, dst_filename)

  def clone(self, mutations = None):
    return tuple_util.clone(self, mutations = mutations)

  @cached_property
  def dst_basename(self):
    return path.basename(self.dst_filename)

  @cached_property
  def dst_dirname(self):
    return path.dirname(self.dst_filename)

  def src_and_dst_are_the_same(self):
    return file_util.files_are_the_same(self.src_filename, self.dst_filename)

  def src_exists(self):
    return path.exists(self.src_filename)

  def dst_exists(self):
    return path.exists(self.dst_filename)
  
check.register_class(dir_operation_item, include_seq = False)

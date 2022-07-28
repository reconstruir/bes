#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from collections import namedtuple

from ..system.check import check
from bes.common.tuple_util import tuple_util
from bes.property.cached_property import cached_property

from .file_util import file_util

class file_resolver_item(namedtuple('file_resolver_item', 'root_dir, filename, index, found_index')):

  def __new__(clazz, root_dir, filename, index, found_index):
    check.check_string(root_dir, allow_none = True)
    check.check_string(filename)
    check.check_int(index)
    check.check_int(found_index)

    return clazz.__bases__[0].__new__(clazz, root_dir, filename, index, found_index)

  def __str__(self):
    return self.filename_abs

  def __repr__(self):
    return str(self)

  def clone(self, mutations = None):
    return tuple_util.clone(self, mutations = mutations)

  @cached_property
  def filename_abs(self):
    return path.join(self.root_dir, self.filename)
  
  @cached_property
  def basename(self):
    return path.basename(self.filename_abs)

  @cached_property
  def dirname(self):
    return path.dirname(self.filename_abs)
  
  @cached_property
  def size(self):
    return file_util.size(self.filename_abs)
  
check.register_class(file_resolver_item, include_seq = False)

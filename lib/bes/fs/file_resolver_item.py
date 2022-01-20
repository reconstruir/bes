#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from collections import namedtuple

from bes.common.check import check
from bes.common.tuple_util import tuple_util

class file_resolver_item(namedtuple('file_resolver_item', 'root_dir, filename, filename_abs, index, found_index')):

  def __new__(clazz, root_dir, filename, filename_abs, index, found_index):
    check.check_string(root_dir, allow_none = True)
    check.check_string(filename)
    check.check_string(filename_abs)
    check.check_int(index)
    check.check_int(found_index)

    return clazz.__bases__[0].__new__(clazz, root_dir, filename, filename_abs, index, found_index)

  def __str__(self):
    return self.filename_abs

  def __repr__(self):
    return str(self)

  def clone(self, mutations = None):
    return tuple_util.clone(self, mutations = mutations)

check.register_class(file_resolver_item, include_seq = False)

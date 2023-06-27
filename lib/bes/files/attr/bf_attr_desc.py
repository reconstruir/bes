#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.system.check import check
from bes.common.tuple_util import tuple_util

from .bf_attr_type_desc_base import bf_attr_type_desc_base

class bf_attr_desc(namedtuple('bf_attr_desc', 'key, name, type_desc, old_keys')):

  def __new__(clazz, key, name, type_desc, old_keys):
    check.check_string(key)
    check.check_string(name)
#    check.check_bf_attr_type_desc(type_desc)
    check.check_string_seq(old_keys, allow_none = True)

    return clazz.__bases__[0].__new__(clazz, key, name, type_desc, old_keys)

  @classmethod
  def _check_cast_func(clazz, obj):
    return tuple_util.cast_seq_to_namedtuple(clazz, obj)
  
  def decode(self, value, allow_none = False):
    return self.type_desc.decode(value, allow_none)

  def encode(self, value, allow_none = False):
    return self.type_desc.encode(value, allow_none)

  def check(self, value, allow_none = False):
    return self.type_desc.check(value, allow_none)
  
check.register_class(bf_attr_desc, include_seq = False, cast_func = bf_attr_desc._check_cast_func)

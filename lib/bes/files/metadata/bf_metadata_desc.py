#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.system.check import check
from bes.version.semantic_version import semantic_version
from bes.common.tuple_util import tuple_util
from bes.property.cached_property import cached_property

from ..attr.bf_attr_desc import bf_attr_desc
from ..attr.bf_attr_type_desc_base import bf_attr_type_desc_base

from .bf_metadata_error import bf_metadata_error
from .bf_metadata_key import bf_metadata_key

class bf_metadata_desc(namedtuple('bf_metadata_desc', 'key, name, getter, type_desc, old_getter')):

  def __new__(clazz, key, name, getter, type_desc, old_getter):
    key = check.check_bf_metadata_key(key)
    check.check_string(name)
    check.check_callable(getter)
#    check.check_bf_attr_type_desc(type_desc)
    check.check_callable(old_getter, allow_none = True)

    return clazz.__bases__[0].__new__(clazz, key, name, getter, type_desc, old_getter)

  @cached_property
  def attr_desc(self):
    return bf_attr_desc(self.key.as_string, self.name, self.type_desc, None)
  
  @classmethod
  def _check_cast_func(clazz, obj):
    return tuple_util.cast_seq_to_namedtuple(clazz, obj)
  
  def get(self, filename):
    return self.getter(filename)

  def decode(self, value):
    return self.attr_desc.decode(value)

  def encode(self, value):
    return self.attr_desc.encode(value)
  
  def check(self, value):
    return self.attr_desc.check(value)
  
check.register_class(bf_metadata_desc, include_seq = False, cast_func = bf_metadata_desc._check_cast_func)

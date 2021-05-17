#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.common.check import check
from bes.property.cached_property import cached_property
from bes.common.type_checked_list import type_checked_list

from .semantic_version import semantic_version
from .semantic_version_error import semantic_version_error

class semantic_version_list(type_checked_list):

  __value_type__ = semantic_version
  
  def __init__(self, values = None):
    super(semantic_version_list, self).__init__(values = values)

  @classmethod
  def cast_value(clazz, value):
    if check.is_string(value):
      return semantic_version(value)
    return value
    
  def sort(self, reverse = False):
    self._values = sorted(self._values, key = lambda v: v._tokens, reverse = reverse)

check.register_class(semantic_version_list, include_seq = False)

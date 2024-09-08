#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.system.check import check
from bes.common.bool_util import bool_util
from bes.system.log import logger

from ..bf_check import bf_check
from ..bf_date import bf_date

from ._detail._bf_attr2_getter_i import _bf_attr2_getter_i

from .bf_attr2_getter_mixin import bf_attr2_getter_mixin

from .bf_attr2_type_desc_datetime import bf_attr2_type_desc_datetime
from .bf_attr2_error import bf_attr2_error
from .bf_attr2_desc_registry import bf_attr2_desc_registry

class bf_attr2_getter_base(_bf_attr2_getter_i, bf_attr2_getter_mixin):

  _log = logger('attr')
  
  def __init__(self, impl):
    assert isinstance(impl, _bf_attr2_getter_i)
    self._impl = impl

  #@abstractmethod
  def has_key(self, filename, key):
    'Return True if filename has an attributed with key.'
    return self._impl.has_key(filename, key)
  
  #@abstractmethod
  def get_bytes(self, filename, key):
    'Return the attribute value with key for filename as bytes.'
    return self._impl.get_bytes(filename, key)

  #@abstractmethod
  def set_bytes(self, filename, key, value):
    'Set the value of attribute with key to value for filename as bytes.'
    self._impl.set_bytes(filename, key, value)
  
  #@abstractmethod
  def remove(self, filename, key):
    'Remove the attirbute with key from filename.'
    self._impl.remove(filename, key)
  
  #@abstractmethod
  def keys(self, filename):
    'Return all the keys set for filename.'
    return self._impl.keys(filename)

  #@abstractmethod
  def clear(self, filename):
    'Create all attributes.'
    self._impl.clear(filename)

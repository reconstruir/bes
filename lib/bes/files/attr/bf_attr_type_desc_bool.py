#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.common.bool_util import bool_util

from .bf_attr_type_desc_base import bf_attr_type_desc_base

from .bf_attr_type_desc_string import bf_attr_type_desc_string

class bf_attr_type_desc_bool(bf_attr_type_desc_base):

  @classmethod
  #@abstractmethod
  def name(clazz):
    'Return the name for this type'
    return 'bool'

  @classmethod
  #@abstractmethod
  def encode(clazz, value, allow_none):
    'Encode value into bytes'
    check.check_bool(value)

    if value == None:
      return b''
    return bf_attr_type_desc_string.encode(str(value), True)

  @classmethod
  #@abstractmethod
  def decode(clazz, value_bytes, allow_none):
    'Decode value_bytes into a value'
    check.check_bytes(value_bytes)
    
    s = value_bytes.decode('utf-8')
    if s == '':
      return None
    return bool_util.parse_bool(s)

  @classmethod
  #@abstractmethod
  def check(clazz, value, allow_none):
    'Return checker function for this type'
    return check.check_bool(value, allow_none = allow_none)

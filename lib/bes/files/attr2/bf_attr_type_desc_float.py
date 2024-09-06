#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.common.number_util import number_util

from .bf_attr_type_desc_base import bf_attr_type_desc_base

from .bf_attr_type_desc_string import bf_attr_type_desc_string

class bf_attr_type_desc_float(bf_attr_type_desc_base):

  @classmethod
  #@abstractmethod
  def name(clazz):
    'Return the name for this type'
    return 'float'

  @classmethod
  #@abstractmethod
  def encode(clazz, value):
    'Encode value into bytes'
    clazz.check(value)

    if value == None:
      return b''
    return bf_attr_type_desc_string.encode(str(value))

  @classmethod
  #@abstractmethod
  def decode(clazz, value_bytes):
    'Decode value_bytes into a value'
    check.check_bytes(value_bytes)
    
    s = value_bytes.decode('utf-8')
    if s == '':
      return None
    return number_util.to_float(s)

  @classmethod
  #@abstractmethod
  def check(clazz, value):
    'Return checker function for this type'
    return check.check_float(value, allow_none = True)

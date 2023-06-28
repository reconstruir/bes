#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from datetime import datetime

from bes.system.check import check

from .bf_attr_type_desc_base import bf_attr_type_desc_base
from .bf_attr_type_desc_string import bf_attr_type_desc_string

class bf_attr_type_desc_datetime(bf_attr_type_desc_base):

  @classmethod
  #@abstractmethod
  def name(clazz):
    'Return the name for this type'
    return 'datetime'

  @classmethod
  #@abstractmethod
  def encode(clazz, value, allow_none):
    'Encode value into bytes'
    clazz.check(value, True)

    if value == None:
      return b''
    return bf_attr_type_desc_string.encode(str(value.timestamp()), True)

  @classmethod
  #@abstractmethod
  def decode(clazz, value_bytes, allow_none):
    'Return decoder function for this type'
    check.check_bytes(value_bytes)

    s = bf_attr_type_desc_string.decode(value_bytes, True)
    timestamp = float(s)
    return datetime.fromtimestamp(timestamp)

  @classmethod
  #@abstractmethod
  def check(clazz, value, allow_none):
    'Return checker function for this type'
    return check.check_datetime(value, allow_none = True)

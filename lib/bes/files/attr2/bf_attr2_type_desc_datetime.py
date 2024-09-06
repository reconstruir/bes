#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from datetime import datetime

from bes.system.check import check

from .bf_attr2_type_desc_base import bf_attr2_type_desc_base
from .bf_attr2_type_desc_string import bf_attr2_type_desc_string

class bf_attr2_type_desc_datetime(bf_attr2_type_desc_base):

  @classmethod
  #@abstractmethod
  def name(clazz):
    'Return the name for this type'
    return 'datetime'

  @classmethod
  #@abstractmethod
  def encode(clazz, value):
    'Encode value into bytes'
    clazz.check(value)

    if value == None:
      return b''
    return bf_attr2_type_desc_string.encode(str(value.timestamp()))

  @classmethod
  #@abstractmethod
  def decode(clazz, value_bytes):
    'Return decoder function for this type'
    check.check_bytes(value_bytes)

    s = bf_attr2_type_desc_string.decode(value_bytes)
    timestamp = float(s)
    return datetime.fromtimestamp(timestamp)

  @classmethod
  #@abstractmethod
  def check(clazz, value):
    'Return checker function for this type'
    return check.check_datetime(value, allow_none = True)

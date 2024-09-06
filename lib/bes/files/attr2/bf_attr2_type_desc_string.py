#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check

from .bf_attr2_type_desc_base import bf_attr2_type_desc_base

class bf_attr2_type_desc_string(bf_attr2_type_desc_base):

  @classmethod
  #@abstractmethod
  def name(clazz):
    'Return the name for this type'
    return 'string'

  @classmethod
  #@abstractmethod
  def encode(clazz, value):
    'Return encoder function for this type'
    clazz.check(value)

    if value == None:
      return b''
    return value.encode('utf-8')

  @classmethod
  #@abstractmethod
  def decode(clazz, value_bytes):
    'Decode value_bytes into a value'
    check.check_bytes(value_bytes)

    return value_bytes.decode('utf-8')

  @classmethod
  #@abstractmethod
  def check(clazz, value):
    'Return checker function for this type'
    return check.check_string(value, allow_none = True)

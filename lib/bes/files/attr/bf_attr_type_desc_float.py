#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check

from .bf_attr_type_desc_base import bf_attr_type_desc_base
from .bf_attr_encoding import bf_attr_encoding

class bf_attr_type_desc_float(bf_attr_type_desc_base):

  @classmethod
  #@abstractmethod
  def name(clazz):
    'Return the name for this type'
    return 'float'

  @classmethod
  #@abstractmethod
  def encode(clazz, value, allow_none):
    'Return encoder function for this type'
    return bf_attr_encoding.encode_float(value, allow_none = allow_none)

  @classmethod
  #@abstractmethod
  def decode(clazz, value_bytes, allow_none):
    'Return decoder function for this type'
    return bf_attr_encoding.decode_float(value_bytes, allow_none = allow_none)

  @classmethod
  #@abstractmethod
  def check(clazz, value, allow_none):
    'Return checker function for this type'
    return check.check_float(value, allow_none = allow_none)

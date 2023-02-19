#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.number_util import number_util
from bes.common.bool_util import bool_util

from bes.system.check import check

class bfile_attr_encoding(object):

  @classmethod
  def decode_int(clazz, value):
    'Decode an int'
    check.check_bytes(value)
    
    return number_util.to_int(value.decode('utf-8'))

  @classmethod
  def encode_int(clazz, value):
    'Decode an int'
    check.check_int(value)

    return str(value).encode('utf-8')
  
  @classmethod
  def decode_float(clazz, value):
    'Decode an int'
    check.check_bytes(value)
    
    return number_util.to_float(value.decode('utf-8'))

  @classmethod
  def encode_float(clazz, value):
    'Decode an float'
    check.check_number(value)

    return str(value).encode('utf-8')
  
  @classmethod
  def decode_string(clazz, value):
    'Decode a string'
    check.check_bytes(value)
    
    return value.decode('utf-8')

  @classmethod
  def encode_string(clazz, value):
    'Decode an string'
    check.check_string(value)

    return value.encode('utf-8')
  
  @classmethod
  def decode_bool(clazz, value):
    'Decode an bool'
    check.check_bytes(value)
    
    return bool_util.parse_bool(value.decode('utf-8'))

  @classmethod
  def encode_bool(clazz, value):
    'Decode an bool'
    check.check_bool(value)

    return str(value).encode('utf-8')

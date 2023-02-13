#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

#from abc import abstractmethod, ABCMeta

from bes.common.number_util import number_util

#from bes.system.compat import with_metaclass
from bes.system.check import check

class bfile_attr_decode(object):

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
    check.check_float(value)

    return str(value).encode('utf-8')
  

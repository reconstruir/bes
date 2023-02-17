#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
import time

from datetime import datetime

from bes.system.check import check
from bes.common.bool_util import bool_util
from bes.system.log import logger
from bes.files.bfile_check import bfile_check

from ..bfile_date import bfile_date

from ._detail._bfile_attr_super_class import _bfile_attr_super_class

from .bfile_attr_error import bfile_attr_error

class _bfile_attr_mixin:

  _log = logger('attr')
  
  @classmethod
  def check_key(clazz, key):
    check.check_string(key)
    
    if ' ' in key:
      raise bfile_attr_error(f'space not supported in key: "{key}"')
    if ':' in key:
      raise bfile_attr_error(f'colon not supported in key: "{key}"')
    return key

  @classmethod
  def get_all(clazz, filename):
    'Return all attributes as a dictionary.'
    keys = clazz.keys(filename)
    result = {}
    for key in keys:
      result[key] = clazz.get_bytes(filename, key)
    return result

  @classmethod
  def set_all(clazz, filename, attributes):
    'Set all file attributes.'
    for key, value in attributes.items():
      clazz.set_bytes(filename, key, value)

  @classmethod
  def get_string(clazz, filename, key, encoding = 'utf-8'):
    'Return the attribute value with key for filename as string.'
    filename = bfile_check.check_file(filename)
    key = clazz.check_key(key)
    value = clazz.get_bytes(filename, key)
    if value == None:
      return None
    return value.decode(encoding)

  @classmethod
  def set_string(clazz, filename, key, value, encoding = 'utf-8'):
    'Set the value of attribute with key to value for filename as string.'
    filename = bfile_check.check_file(filename)
    key = clazz.check_key(key)
    check.check_string(value)
    clazz.set_bytes(filename, key, value.encode(encoding))

  @classmethod
  def get_date(clazz, filename, key):
    'Return the attribute value with key for filename as string.'
    filename = bfile_check.check_file(filename)
    key = clazz.check_key(key)
    value = clazz.get_string(filename, key)
    if value == None:
      return None
    timestamp = float(value)
    return datetime.fromtimestamp(timestamp)

  @classmethod
  def set_date(clazz, filename, key, value, encoding = 'utf-8'):
    'Set the value of attribute with key to value for filename as string.'
    filename = bfile_check.check_file(filename)
    key = clazz.check_key(key)
    check.check(value, datetime)
    
    clazz.set_string(filename, key, str(value.timestamp()))

  @classmethod
  def get_bool(clazz, filename, key):
    'Return the attribute value with key for filename as string.'
    filename = bfile_check.check_file(filename)
    key = clazz.check_key(key)
    value = clazz.get_string(filename, key)
    if value == None:
      return None
    return bool_util.parse_bool(value)

  @classmethod
  def set_bool(clazz, filename, key, value, encoding = 'utf-8'):
    'Set the value of attribute with key to value for filename as string.'
    filename = bfile_check.check_file(filename)
    key = clazz.check_key(key)
    check.check_bool(value)
    
    clazz.set_string(filename, key, str(value).lower())
    
  @classmethod
  def get_int(clazz, filename, key):
    'Return the attribute value with key for filename as string.'
    filename = bfile_check.check_file(filename)
    key = clazz.check_key(key)
    
    value = clazz.get_string(filename, key)
    if value == None:
      return None
    return int(value)

  @classmethod
  def set_int(clazz, filename, key, value, encoding = 'utf-8'):
    'Set the value of attribute with key to value for filename as string.'
    filename = bfile_check.check_file(filename)
    key = clazz.check_key(key)
    check.check_int(value)
    
    clazz.set_string(filename, key, str(value))

  @classmethod
  def get_float(clazz, filename, key):
    'Return the attribute value with key for filename as string.'
    filename = bfile_check.check_file(filename)
    key = clazz.check_key(key)
    
    value = clazz.get_string(filename, key)
    if value == None:
      return None
    return float(value)

  @classmethod
  def set_float(clazz, filename, key, value, encoding = 'utf-8'):
    'Set the value of attribute with key to value for filename as string.'
    filename = bfile_check.check_file(filename)
    key = clazz.check_key(key)
    check.check_float(value)
    
    clazz.set_string(filename, key, str(value))
    
class bfile_attr(_bfile_attr_super_class, _bfile_attr_mixin):
  pass

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

  _log = logger('attributes')
  
  @classmethod
  def _check_key(clazz, key):
    check.check_string(key)
    if ' ' in key:
      raise bfile_attr_error('space not supported in key: \"{}\"'.format(key))
    if ':' in key:
      raise bfile_attr_error('colon not supported in key: \"{}\"'.format(key))
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
    key = clazz._check_key(key)
    value = clazz.get_bytes(filename, key)
    if value == None:
      return None
    return value.decode(encoding)

  @classmethod
  def set_string(clazz, filename, key, value, encoding = 'utf-8'):
    'Set the value of attribute with key to value for filename as string.'
    filename = bfile_check.check_file(filename)
    key = clazz._check_key(key)
    check.check_string(value)
    clazz.set_bytes(filename, key, value.encode(encoding))

  @classmethod
  def get_date(clazz, filename, key):
    'Return the attribute value with key for filename as string.'
    filename = bfile_check.check_file(filename)
    key = clazz._check_key(key)
    value = clazz.get_string(filename, key)
    if value == None:
      return None
    timestamp = float(value)
    return datetime.fromtimestamp(timestamp)

  @classmethod
  def set_date(clazz, filename, key, value, encoding = 'utf-8'):
    'Set the value of attribute with key to value for filename as string.'
    filename = bfile_check.check_file(filename)
    key = clazz._check_key(key)
    check.check(value, datetime)
    
    clazz.set_string(filename, key, str(value.timestamp()))

  @classmethod
  def get_bool(clazz, filename, key):
    'Return the attribute value with key for filename as string.'
    filename = bfile_check.check_file(filename)
    key = clazz._check_key(key)
    value = clazz.get_string(filename, key)
    if value == None:
      return None
    return bool_util.parse_bool(value)

  @classmethod
  def set_bool(clazz, filename, key, value, encoding = 'utf-8'):
    'Set the value of attribute with key to value for filename as string.'
    filename = bfile_check.check_file(filename)
    key = clazz._check_key(key)
    check.check_bool(value)
    
    clazz.set_string(filename, key, str(value).lower())
    
  @classmethod
  def get_int(clazz, filename, key):
    'Return the attribute value with key for filename as string.'
    filename = bfile_check.check_file(filename)
    key = clazz._check_key(key)
    
    value = clazz.get_string(filename, key)
    if value == None:
      return None
    return int(value)

  @classmethod
  def set_int(clazz, filename, key, value, encoding = 'utf-8'):
    'Set the value of attribute with key to value for filename as string.'
    filename = bfile_check.check_file(filename)
    key = clazz._check_key(key)
    check.check_int(value)
    
    clazz.set_string(filename, key, str(value))

  @classmethod
  def get_bytes_mtime_cached(clazz, filename, key, value_maker):
    filename = bfile_check.check_file(filename)
    check.check_string(key)
    check.check_callable(value_maker)

    clazz._log.log_method_d()

#    if fallback and not os.access(filename, os.R_OK):
#      clazz._log.log_d('get_bytes:{filename}:{key}: no read access')
#      return value_maker(filename)
    
    mtime_key = clazz._make_mtime_key(key)
    attr_mtime = clazz.get_date(filename, mtime_key)
    file_mtime = bfile_date.get_modification_date(filename)
    value = None
    
    label = f'get_bytes:{filename}:{key}'

    if file_mtime == attr_mtime:
      return clazz.get_bytes(filename, key)
    
    value = value_maker(filename)
    if value == None:
      raise bfile_attr_error(f'value should never be None')

    clazz.set_bytes(filename, key, value)
    clazz.set_date(filename, mtime_key, file_mtime)
    # setting the date in the line above has the side effect
    # of changing the mtime in some implementations.  so we
    # force it to be what it was right after setting the value
    # which is in the past (usually microseconds) but guaranteed
    # to match what what was set in set_date()
    bfile_date.set_modification_date(filename, file_mtime)
    return value

  @classmethod
  def _make_mtime_key(clazz, key):
    return f'__bes_mtime_{key}__'
    
class bfile_attr(_bfile_attr_super_class, _bfile_attr_mixin):
  pass

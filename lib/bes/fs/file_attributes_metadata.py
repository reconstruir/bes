#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os

from bes.common.bool_util import bool_util
from bes.system.check import check
from bes.system.log import logger

from .file_attributes import file_attributes
from .file_attributes_error import file_attributes_permission_error
from .file_mime import file_mime
from .file_path import file_path
from .file_util import file_util

class file_attributes_metadata(object):

  _log = logger('file_attributes_metadata')
  
  _KEY_BES_MIME_TYPE = 'bes_mime_type'
  
  @classmethod
  def get_bytes(clazz, filename, key, value_maker, fallback = False):
    check.check_string(filename)
    check.check_string(key)
    check.check_function(value_maker)

    clazz._log.log_method_d()

    if fallback and not os.access(filename, os.R_OK):
      clazz._log.log_d('get_bytes:{filename}:{key}: no read access')
      return value_maker()
    
    mtime_key = clazz._make_mtime_key(key)
    attr_mtime = file_attributes.get_date(filename, mtime_key)
    file_mtime = file_util.get_modification_date(filename)

    label = f'get_bytes:{filename}:{key}'
    
    clazz._log.log_d(f'{label}: attr_mtime={attr_mtime} file_mtime={file_mtime}')
    if attr_mtime == None:
      value = value_maker()
      if fallback and not os.access(filename, os.W_OK):
        clazz._log.log_d(f'{label}: no write access')
        return value
      clazz._log.log_d(f'{label}: creating new value "{value}"')
      clazz._refresh_value(filename, key, value, mtime_key)
      return value

    if attr_mtime == file_mtime:
      if file_attributes.has_key(filename, key):
        value = file_attributes.get_bytes(filename, key)
        clazz._log.log_d(f'{label}: using cached value "{value}"')
        return value

    value = value_maker()
    if fallback and not os.access(filename, os.W_OK):
      clazz._log.log_d(f'{label}: no write access')
      return value
    clazz._refresh_value(filename, key, value, mtime_key)
    clazz._log.log_d(f'{label}: refreshing value "{value}"')
    return value

  @classmethod
  def _refresh_value(clazz, filename, key, value, mtime_key):
    file_attributes.set_bytes(filename, key, value)
    file_mtime = file_util.get_modification_date(filename)
    file_attributes.set_date(filename, mtime_key, file_mtime)
    # setting the date in the line above has the side effect
    # of changing the mtime in some implementations.  so we
    # force it to be what it was right after setting the value
    # which is in the past (usually microseconds) but guranteed
    # to match what what was set in set_date()
    file_util.set_modification_date(filename, file_mtime)
    
  @classmethod
  def get_string(clazz, filename, key, value_maker, fallback = False):
    check.check_string(filename)
    check.check_string(key)
    check.check_function(value_maker)
    check.check_bool(fallback)

    value = clazz.get_bytes(filename, key, value_maker, fallback = fallback)
    if value == None:
      return None
    return value.decode('utf-8')

  @classmethod
  def get_bool(clazz, filename, key, value_maker, fallback = False):
    check.check_string(filename)
    check.check_string(key)
    check.check_function(value_maker)
    check.check_bool(fallback)

    value = clazz.get_string(filename, key, value_maker, fallback = fallback)
    if value == None:
      return None
    return bool_util.parse_bool(value)
  
  @classmethod
  def get_mime_type(clazz, filename, fallback = False):
    check.check_string(filename)
    check.check_bool(fallback)

    def _value_maker():
      return file_mime.mime_type(filename).encode('utf-8')
    return clazz.get_string(filename, clazz._KEY_BES_MIME_TYPE, _value_maker, fallback = fallback)

  @classmethod
  def _make_mtime_key(clazz, key):
    return '__bes_mtime_{}__'.format(key)

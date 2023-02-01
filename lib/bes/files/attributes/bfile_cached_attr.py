#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
import time

from datetime import datetime

from bes.system.check import check
from bes.common.bool_util import bool_util
from bes.system.log import logger
from bes.files.bfile_check import bfile_check

from ..bfile_date import bfile_date

from .bfile_attr import bfile_attr
from .bfile_attr_error import bfile_attr_error
from .bfile_attr_getter_base import bfile_attr_getter_base

class bfile_cached_attr(bfile_attr):

  _log = logger('attr')

  @classmethod
  def _get_bytes_mtime_cached(clazz, filename, key, value_maker):
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

  class _getter_item(object):
 
    def __init__(self, getter_class):
      check.check_class(getter_class, bfile_attr_getter_base)

      self._getter_class = getter_class
      self.cache = {}

    @cached_property
    def getter(self):
      return self._getter_class()
  
  _getters = {}
  @classmethod
  def register_attr_getter(clazz, getter_class):
    check.check_class(getter_class, bfile_attr_getter_base)

    domain = getter_class.domain()
    if not check.is_string(domain):
      raise bfile_error(f'domain should be a string: "{domain}" - {type(domain)}')
    keys = getter_class.keys()
    if not check.is_dict(keys):
      raise bfile_error(f'keys should be a dict: "{keys}" - {type(keys)}')
    for key, version in keys.items():
      if not check.is_string(key):
        raise bfile_error(f'key should be a string: "{key}" - {type(key)}')
      if not check.is_string(version):
        raise bfile_error(f'version should be a string: "{version}" - {type(version)}')
      getter_key = clazz._make_metadata_getter_key(domain, key, version)
      if getter_key in clazz._getters:
        raise bfile_error(f'getter already registered: "{getter_key}"')
      clazz._getters[getter_key] = clazz._getter_item(getter_class)

  @classmethod
  def _make_metadata_getter_key(clazz, domain, key, version):
    return f'{domain}.{key}.{version}'

  @classmethod
  def _get_metadata_getter_item(clazz, domain, key, version):
    getter_key = clazz._make_metadata_getter_key(domain, key, version)
    return clazz._getters.get(getter_key, None)
  

  '''
  @property
  def _cache_key(self):
    return f'{self.hashed_filename_sha256}_{self.modification_date_timestamp}'
  
  @property
  def media_type(self):
    return file_attributes_metadata.get_media_type(self._filename,
                                                   fallback = True,
                                                   cached = True)

  @property
  def mime_type(self):
    return file_attributes_metadata.get_mime_type(self._filename,
                                                  fallback = True,
                                                  cached = True)

  @property
  def is_media(self):
    return self.is_file and self.media_type in ( 'image', 'video' )

  @property
  def is_image(self):
    return self.is_file and self.media_type in ( 'image' )

  @property
  def is_video(self):
    return self.is_file and self.media_type in ( 'video' )

  class _getter_item(object):
 
    def __init__(self, getter_class):
      self._getter_class = getter_class
      self.cache = {}

    @cached_property
    def getter(self):
      return self._getter_class()

  @classmethod
  def _make_mtime_key(clazz, key):
    return f'__bes_mtime_{key}__'
    
  _getters = {}
  @classmethod
  def register_metadata_getter(clazz, getter_class):
    check.check_class(getter_class, bfile_attr_getter_base)

    domain = getter_class.domain()
    if not check.is_string(domain):
      raise bfile_error(f'domain should be a string: "{domain}" - {type(domain)}')
    keys = getter_class.keys()
    if not check.is_dict(keys):
      raise bfile_error(f'keys should be a dict: "{keys}" - {type(keys)}')
    for key, version in keys.items():
      if not check.is_string(key):
        raise bfile_error(f'key should be a string: "{key}" - {type(key)}')
      if not check.is_string(version):
        raise bfile_error(f'version should be a string: "{version}" - {type(version)}')
      getter_key = clazz._make_metadata_getter_key(domain, key, version)
      if getter_key in clazz._getters:
        raise bfile_error(f'getter already registered: "{getter_key}"')
      clazz._getters[getter_key] = clazz._getter_item(getter_class)

  @classmethod
  def _make_metadata_getter_key(clazz, domain, key, version):
    return f'{domain}.{key}.{version}'

  @classmethod
  def _get_metadata_getter_item(clazz, domain, key, version):
    getter_key = clazz._make_metadata_getter_key(domain, key, version)
    return clazz._getters.get(getter_key, None)

  def get_metadata_value(self, domain, key, version, cached = False):
    check.check_string(domain)
    check.check_string(key)
    check.check_string(version)
    check.check_bool(cached)

    getter_item = self._get_metadata_getter_item(domain, key, version)
    if not getter_item:
      raise bfile_error(f'no getter registered: "{domain.key.version}"')
    if cached:
      cache_key = self._cache_key
      if not cache_key in getter_item.cache:
        value = clazz.get_value(filename, key, fallback = fallback, cached = False)
        getter_item.cache[cache_key] = value
      return getter_item.cache[cache_key]
#    filename, domain, key, version
    def _value_maker(f):
      return getter_item.getter.get_value(clazz, f)
    value = clazz.get_bytes(filename, key, _value_maker, fallback = fallback)
    if value == None:
      return None
    return getter_item.getter.decode_value(value)

#    if not os.access(self._filename, os.R_OK):
#      raise bfile_permission_error(f'No read access: {filename}')
  
  def get_metadata_bytes(self, domain, key, version):
    check.check_string(filename)
    check.check_string(key)
    check.check_callable(value_maker)

    clazz._log.log_method_d()

    if fallback and not os.access(filename, os.R_OK):
      clazz._log.log_d('get_bytes:{filename}:{key}: no read access')
      return value_maker(filename)
    
    mtime_key = clazz._make_mtime_key(key)
    attr_mtime = file_attributes.get_date(filename, mtime_key)
    file_mtime = file_util.get_modification_date(filename)

    label = f'get_bytes:{filename}:{key}'
    
    clazz._log.log_d(f'{label}: attr_mtime={attr_mtime} file_mtime={file_mtime}')
    if attr_mtime == None:
      value = value_maker(filename)
      clazz._log.log_d(f'{label}: creating new value "{value}"')
      if fallback and not os.access(filename, os.W_OK):
        clazz._log.log_d(f'{label}: no write access')
        return value
      if value == None:
        return None
      clazz._refresh_value(filename, key, value, mtime_key)
      return value

    if attr_mtime == file_mtime:
      if file_attributes.has_key(filename, key):
        value = file_attributes.get_bytes(filename, key)
        clazz._log.log_d(f'{label}: using cached value "{value}"')
        return value

    value = value_maker(filename)
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
'''
  

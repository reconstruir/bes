#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
import os

from bes.common.bool_util import bool_util
from bes.common.hash_util import hash_util
from bes.common.time_util import time_util
from bes.system.check import check
from bes.system.log import logger
from bes.property.cached_property import cached_property

from .file_attributes import file_attributes
from .file_attributes_error import file_attributes_permission_error
from .file_mime import file_mime
from .file_path import file_path
from .file_util import file_util

from .file_metadata_getter_base import file_metadata_getter_base
from .file_metadata_getter_checksum_md5 import file_metadata_getter_checksum_md5
from .file_metadata_getter_checksum_sha1 import file_metadata_getter_checksum_sha1
from .file_metadata_getter_checksum_sha256 import file_metadata_getter_checksum_sha256
from .file_metadata_getter_media_type import file_metadata_getter_media_type
from .file_metadata_getter_mime_type import file_metadata_getter_mime_type

class file_attributes_metadata(object):

  _log = logger('file_attributes_metadata')
  
  @classmethod
  def get_bytes(clazz, filename, key, value_maker, fallback = False):
    check.check_string(filename)
    check.check_string(key)
    check.check_function(value_maker)

    clazz._log.log_method_d()

    if fallback and not os.access(filename, os.R_OK):
      clazz._log.log_d('get_bytes:{filename}:{key}: no read access')
      return value_maker(filename)
    
    mtime_key = f'__bes_mtime_{key}__'
    attr_mtime = file_attributes.get_date(filename, mtime_key)
    file_mtime = file_util.get_modification_date(filename)

    label = f'get_bytes:{filename}:{key}'
    
    clazz._log.log_d(f'{label}: attr_mtime={attr_mtime} file_mtime={file_mtime}')
    if attr_mtime == None:
      value = value_maker(filename)
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
  def _make_cache_key(clazz, filename):
    hashed_filename = hash_util.hash_string_sha256(filename)
    mtime_string = time_util.timestamp(when = file_util.get_modification_date(filename))
    return f'{hashed_filename}_{mtime_string}'

  class _getter_item(object):

    def __init__(self, getter_class):
      self._getter_class = getter_class
      self.cache = {}

    @cached_property
    def getter(self):
      return self._getter_class()
      
  _getters = {}
  @classmethod
  def register_getter(clazz, getter_class):
    check.check_class(getter_class, file_metadata_getter_base)

    name = getter_class.name()
    if name in clazz._getters:
      raise RuntimeError(f'Getter already registered: \"{name}\"')
    clazz._getters[name] = clazz._getter_item(getter_class)

  @classmethod
  def get_value(clazz, name, filename, fallback = False, cached = False):
    check.check_string(name)
    check.check_string(filename)
    check.check_bool(fallback)
    check.check_bool(cached)

    if not name in clazz._getters:
      raise KeyError(f'No getter registered for: \"{name}\"')
    getter_item = clazz._getters[name]

    if cached:
      cache_key = clazz._make_cache_key(filename)
      if not cache_key in getter_item.cache:
        value = clazz.get_value(name, filename, fallback = fallback, cached = False)
        getter_item.cache[cache_key] = value
      return getter_item.cache[cache_key]
    
    def _value_maker(f):
      return getter_item.getter.get_value(clazz, f)
    value = clazz.get_bytes(filename, name, _value_maker, fallback = fallback)
    return getter_item.getter.decode_value(value)

  @classmethod
  def get_checksum_sha256(clazz, filename, fallback = False, cached = False):
    return clazz.get_value('bes_checksum_sha256', filename, fallback = fallback, cached = cached)

  @classmethod
  def get_checksum_sha1(clazz, filename, fallback = False, cached = False):
    return clazz.get_value('bes_checksum_sha1', filename, fallback = fallback, cached = cached)

  @classmethod
  def get_checksum_md5(clazz, filename, fallback = False, cached = False):
    return clazz.get_value('bes_checksum_md5', filename, fallback = fallback, cached = cached)
  
  @classmethod
  def get_mime_type(clazz, filename, fallback = False, cached = False):
    return clazz.get_value('bes_mime_type', filename, fallback = fallback, cached = cached)

  @classmethod
  def get_media_type(clazz, filename, fallback = False, cached = False):
    return clazz.get_value('bes_media_type', filename, fallback = fallback, cached = cached)
  
check.register_class(file_attributes_metadata, include_seq = False)

file_attributes_metadata.register_getter(file_metadata_getter_checksum_md5)
file_attributes_metadata.register_getter(file_metadata_getter_checksum_sha1)
file_attributes_metadata.register_getter(file_metadata_getter_checksum_sha256)
file_attributes_metadata.register_getter(file_metadata_getter_media_type)
file_attributes_metadata.register_getter(file_metadata_getter_mime_type)

#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
import os

from bes.common.bool_util import bool_util
from bes.common.hash_util import hash_util
from bes.common.time_util import time_util
from bes.fs.file_check import file_check
from bes.property.cached_property import cached_property
from bes.system.check import check
from bes.system.log import logger

from .file_attributes import file_attributes
from .file_attributes_error import file_attributes_permission_error
from .file_mime import file_mime
from bes.files.bf_path import bf_path
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
    
  @classmethod
  def get_string(clazz, filename, key, value_maker, fallback = False):
    check.check_string(filename)
    check.check_string(key)
    check.check_callable(value_maker)
    check.check_bool(fallback)

    value = clazz.get_bytes(filename, key, value_maker, fallback = fallback)
    if value == None:
      return None
    return value.decode('utf-8')

  @classmethod
  def get_bool(clazz, filename, key, value_maker, fallback = False):
    check.check_string(filename)
    check.check_string(key)
    check.check_callable(value_maker)
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

  @classmethod
  def _make_mtime_key(clazz, key):
    return f'__bes_mtime_{key}__'

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
  def get_value(clazz, filename, key, fallback = False, cached = False):
    check.check_string(filename)
    check.check_string(key)
    check.check_bool(fallback)
    check.check_bool(cached)

    if not key in clazz._getters:
      raise KeyError(f'No getter registered for: \"{key}\"')
    getter_item = clazz._getters[key]

    if cached:
      cache_key = clazz._make_cache_key(filename)
      if not cache_key in getter_item.cache:
        value = clazz.get_value(filename, key, fallback = fallback, cached = False)
        getter_item.cache[cache_key] = value
      return getter_item.cache[cache_key]
    
    def _value_maker(f):
      return getter_item.getter.get_value(clazz, f)
    value = clazz.get_bytes(filename, key, _value_maker, fallback = fallback)
    if value == None:
      return None
    return getter_item.getter.decode_value(value)

  @classmethod
  def remove_value(clazz, filename, key):
    check.check_string(filename)
    check.check_string(key)
    
    getter_item = clazz._getters.get(key, None)
    if getter_item:
      cache_key = clazz._make_cache_key(filename)
      if cache_key in getter_item.cache:
        del getter_item.cache[cache_key]

    mtime_key = clazz._make_mtime_key(key)
    if file_attributes.has_key(filename, mtime_key):
      file_attributes.remove(filename, mtime_key)
    if file_attributes.has_key(filename, key):
      file_attributes.remove(filename, key)

  @classmethod
  def remove_values(clazz, filename, func):
    filename = file_check.check_file(filename)
    check.check_callable(func)
    
    keys = [ key for key in file_attributes.keys(filename) if func(key) ]
    for key in keys:
      clazz.remove_value(filename, key)
      
  @classmethod
  def get_checksum_sha256(clazz, filename, fallback = False, cached = False):
    return clazz.get_value(filename, 'bes_checksum_sha256', fallback = fallback, cached = cached)

  @classmethod
  def get_checksum_sha1(clazz, filename, fallback = False, cached = False):
    return clazz.get_value(filename, 'bes_checksum_sha1', fallback = fallback, cached = cached)

  @classmethod
  def get_checksum_md5(clazz, filename, fallback = False, cached = False):
    return clazz.get_value(filename, 'bes_checksum_md5', fallback = fallback, cached = cached)
  
  @classmethod
  def get_mime_type(clazz, filename, fallback = False, cached = False):
    return clazz.get_value(filename, 'bes_mime_type', fallback = fallback, cached = cached)

  @classmethod
  def get_media_type(clazz, filename, fallback = False, cached = False):
    return clazz.get_value(filename, 'bes_media_type', fallback = fallback, cached = cached)

  @classmethod
  def get_metadata(clazz, filename, key, fallback = True, cached = True):
    method_name = f'get_{key}'
    method = getattr(clazz, method_name, None)
    if method == None:
      raise RuntimeError(f'No method "{method_name}" found in "{clazz}"')
    return method(filename, fallback = fallback, cached = cached)

  @classmethod
  def media_type_matches(clazz, filename, media_types):
    filename = file_check.check_file(filename)
    check.check_string_seq(media_types)
    
    media_type = clazz.get_metadata(filename, 'media_type')
    if not media_type:
      return False
    return media_type in media_types
  
  @classmethod
  def is_media(clazz, filename):
    return clazz.media_type_matches(filename, ( 'image', 'video' ))

  @classmethod
  def is_video(clazz, filename):
    return clazz.media_type_matches(filename, ( 'video', ))
  
  @classmethod
  def is_image(clazz, filename):
    return clazz.media_type_matches(filename, ( 'image', ))

  @classmethod
  def mime_type_matches(clazz, filename, mime_types):
    filename = file_check.check_file(filename)
    check.check_string_seq(mime_types)
    
    mime_type = clazz.get_metadata(filename, 'mime_type')
    if not mime_type:
      return False
    return mime_type in mime_types
  
check.register_class(file_attributes_metadata, include_seq = False)

file_attributes_metadata.register_getter(file_metadata_getter_checksum_md5)
file_attributes_metadata.register_getter(file_metadata_getter_checksum_sha1)
file_attributes_metadata.register_getter(file_metadata_getter_checksum_sha256)
file_attributes_metadata.register_getter(file_metadata_getter_media_type)
file_attributes_metadata.register_getter(file_metadata_getter_mime_type)

#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import time
import os
from os import path
from datetime import datetime
from collections import namedtuple

from bes.common.hash_util import hash_util
from bes.common.time_util import time_util
from bes.property.cached_property import cached_property
from bes.system.check import check
from bes.system.log import logger

from .bfile_cached_attribute import bfile_cached_attribute
from .bfile_error import bfile_error
from .bfile_filename import bfile_filename
from .bfile_permission_error import bfile_permission_error

class bfile_entry(object):

  _log = logger('bfile_entry')
  
  def __init__(self, filename):
    self._filename = filename
    self._stat = bfile_cached_attribute(self._filename, lambda f: os.stat(filename, follow_symlinks = True))

  @cached_property
  def filename(self):
    return self._filename

  @cached_property
  def filename_lowercase(self):
    return self.filename.lower()
  
  @cached_property
  def dirname(self):
    return path.dirname(self._filename)

  @cached_property
  def dirname_lowercase(self):
    return self.dirname.lower()
  
  @cached_property
  def basename(self):
    return path.basename(self._filename)

  @cached_property
  def extension(self):
    return bfile_filename.extension(self._filename)

  @cached_property
  def extension_lowercase(self):
    return self.extension.lower()
  
  @property
  def exists(self):
    return  path.exists(self._filename)

  @property
  def is_readable(self):
    return os.access(self._filename, os.R_OK)

  @property
  def is_writable(self):
    return os.access(self._filename, os.W_OK)

  @property
  def is_executable(self):
    return os.access(self._filename, os.F_OK)
  
  _access_result = namedtuple('_access_result', 'exists, can_read, can_write, can_execute')
  @property
  def access(self):
    exists = os.access(self._filename, os.F_OK)
    if exists:
      can_read = os.access(self._filename, os.R_OK)
      can_write = os.access(self._filename, os.W_OK)
      can_execute = os.access(self._filename, os.X_OK)
    else:
      can_read = False
      can_write = False
      can_execute = False
    return self._access_result(exists, can_read, can_write, can_execute)
  
  @property
  def stat(self):
    return self._stat.value

  @cached_property
  def hashed_filename_sha256(self):
    return hash_util.hash_string_sha256(self._filename)
  
  @cached_property
  def basename_lowercase(self):
    return self.basename.lower()

  @property
  def is_dir(self):
    return path.isdir(self._filename)
  
  @property
  def is_file(self):
    return path.isfile(self._filename)
  
  @property
  def size(self):
    return self.stat.st_size
  
  @property
  def modification_date(self):
    ts = path.getmtime(self._filename)
    return datetime.fromtimestamp(ts)

  @modification_date.setter
  def modification_date(self, mtime):
    check.check_datetime(mtime)

    ts = mtime.timestamp()
    os.utime(self._filename, ( ts, ts ))

  @property
  def modification_date_timestamp(self):
    return time_util.timestamp(when = self.modification_date)

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
    check.check_class(getter_class, bfile_metadata_getter_base)

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
#file_entry.register_metadata_getter('cv', 'faces', '1.0.0', clazz)

fi = file_entry('/foo/caca.jpg')
fi.tags.is_favorite = True
fi.tags.checksum_sha256

fi.get_metadata('checksum', 'sha256', '1.0.0')
'''
  
check.register_class(bfile_entry, include_seq = False)

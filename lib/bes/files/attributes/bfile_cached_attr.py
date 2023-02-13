#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
import time
import os.path as path

from datetime import datetime
from collections import namedtuple

from bes.common.bool_util import bool_util
from bes.property.cached_property import cached_property
from bes.system.check import check
from bes.system.log import logger

from ..bfile_date import bfile_date
from ..bfile_check import bfile_check

from .bfile_attr import bfile_attr
from .bfile_attr_error import bfile_attr_error
from .bfile_attr_factory_base import bfile_attr_factory_base
from .bfile_attr_factory_registry import bfile_attr_factory_registry
from .bfile_attr_handler import bfile_attr_handler
from .bfile_attr_handler_list import bfile_attr_handler_list

class bfile_cached_attr(bfile_attr):

  @classmethod
  def get_cached_bytes(clazz, filename, key, value_maker):
    'Return the attribute value with key for filename as bytes.'
    filename = bfile_check.check_file(filename)
    key = clazz.check_key(key)
    check.check_callable(value_maker)

    value, _, _ = clazz._do_get_cached_bytes(filename, key, value_maker)
    return value

  @classmethod
  def get_cached_string(clazz, filename, key, value_maker, encoding = 'utf-8'):
    filename = bfile_check.check_file(filename)
    key = clazz.check_key(key)
    check.check_callable(value_maker)
    clazz.check_string(encoding)
    
    value = clazz.get_cached_bytes(filename, key, value_maker)
    if value == None:
      return None
    return value.decode(encoding)

  @classmethod
  def _make_mtime_key(clazz, key):
    return f'__bes_mtime_{key}__'

  _get_cached_bytes_result = namedtuple('_get_cached_bytes_result', 'value, mtime, is_cached')
  @classmethod
  def _do_get_cached_bytes(clazz, filename, key, value_maker):
    'Return the attribute value with key for filename as bytes.'
    filename = bfile_check.check_file(filename)
    key = clazz.check_key(key)
    check.check_callable(value_maker)

    clazz._log.log_method_d()

    mtime_key = clazz._make_mtime_key(key)
    attr_mtime = clazz.get_date(filename, mtime_key)
    file_mtime = bfile_date.get_modification_date(filename)
    value = None
    
    label = f'get_cached_bytes:{filename}:{key}'

    if file_mtime == attr_mtime:
      value = clazz.get_bytes(filename, key)
      return clazz._get_cached_bytes_result(value, file_mtime, True)
    
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
    return clazz._get_cached_bytes_result(value, file_mtime, False)
  
  _cached_metadata = {}
  class _cached_metadata_item(object):

    def __init__(self):
      self._last_mtime = None
      self._value = None
      self._count = 0

  @classmethod
  def _get_cached_metadata_item(clazz, filename, factory_key):
    if filename not in clazz._cached_metadata:
      clazz._cached_metadata[filename] = {}
    file_dict = clazz._cached_metadata[filename]
    if not factory_key in file_dict:
      file_dict[factory_key] = clazz._cached_metadata_item()
    return file_dict[factory_key]
    
  @classmethod
  def get_cached_metadata(clazz, filename, domain, key, version):
    filename = bfile_check.check_file(filename)
    check.check_string(domain)
    check.check_string(key)
    check.check_string(version)

    handler = bfile_attr_factory_registry.get_handler(domain, key, version)
    item = clazz._get_cached_metadata_item(filename, handler.factory_key)
    current_mtime = bfile_date.get_modification_date(filename)
    clazz._log.log_d(f'get_cached_metadata: filename={filename} current_mtime={current_mtime} last_mtime={item._last_mtime}')
    if item._last_mtime != None:
      assert not item._last_mtime > current_mtime
      if current_mtime <= item._last_mtime:
        assert item._value != None
        return item._value
    value_bytes, mtime, _ = clazz._do_get_cached_bytes(filename, handler.factory_key, handler.getter)
    value = handler.decoder(value_bytes)
    item._last_mtime = mtime
    item._value = value
    assert item._value != None
    item._count += 1
    assert item._value != None
    return item._value
    
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

  def get_metadata_value(self, domain, key, version, cached = False):
    check.check_string(domain)
    check.check_string(key)
    check.check_string(version)
    check.check_bool(cached)

    factory_item = self._get_factory_item(domain, key, version)
    if not factory_item:
      raise bfile_error(f'no getter registered: "{domain.key.version}"')
    if cached:
      cache_key = self._cache_key
      if not cache_key in factory_item.cache:
        value = clazz.get_value(filename, key, fallback = fallback, cached = False)
        factory_item.cache[cache_key] = value
      return factory_item.cache[cache_key]
#    filename, domain, key, version
    def _value_maker(f):
      return factory_item.getter.get_value(clazz, f)
    value = clazz.get_bytes(filename, key, _value_maker, fallback = fallback)
    if value == None:
      return None
    return factory_item.getter.decode_value(value)
'''
  

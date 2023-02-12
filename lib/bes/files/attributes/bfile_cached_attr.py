#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
import time

from datetime import datetime

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

    clazz._log.log_method_d()

    mtime_key = clazz._make_mtime_key(key)
    attr_mtime = clazz.get_date(filename, mtime_key)
    file_mtime = bfile_date.get_modification_date(filename)
    value = None
    
    label = f'get_cached_bytes:{filename}:{key}'

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

  class _factory_item(object):
 
    def __init__(self, factory_class):
      self._factory_class = factory_class
      self.cache = {}

    @cached_property
    def factory(self):
      return self._factory_class()

  _factories = {}
  @classmethod
  def register_attr_factory(clazz, factory_class):
    check.check_class(factory_class, bfile_attr_factory_base)

    raw_handlers_list = factory_class.handlers()
    try:
      handlers = check.check_bfile_attr_handler_list(raw_handlers_list)
    except TypeError as ex:
      raise bfile_attr_error(f'handlers should be a sequence of "bfile_attr_handler" or tuples: "{raw_handlers_list}" - {type(raw_handlers_list)}')
    for handler in handlers:
      if handler.factory_key in clazz._factories:
        raise bfile_error(f'getter already registered: "{handler.factory_key}"')
      clazz._factories[handler.key] = clazz._factory_item(factory_class)

  @classmethod
  def _get_factory_item(clazz, domain, key, version):
    handler_key = bfile_attr_handler.make_factory_key(domain, key, version)
    return clazz._factories.get(handler_key, None)

  '''
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
  

#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.system.log import logger

from ..bfile_date import bfile_date
from ..bfile_check import bfile_check

from .bfile_attr_factory_registry import bfile_attr_factory_registry

from .bfile_attr_mtime_cached import bfile_attr_mtime_cached

class bfile_attr_metadata(bfile_attr_mtime_cached):

  @classmethod
  def get_cached_metadata(clazz, filename, domain, group, name, version):
    filename = bfile_check.check_file(filename)
    check.check_string(domain)
    check.check_string(group)
    check.check_string(name)
    check.check_string(version)

    handler = bfile_attr_factory_registry.get_handler(domain, group, name, version)
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
  
  '''
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

  def get_metadata_value(self, domain, group, name, version, cached = False):
    check.check_string(domain)
    check.check_string(key)
    check.check_string(version)
    check.check_bool(cached)

    factory_item = self._get_factory_item(domain, group, name, version)
    if not factory_item:
      raise bfile_error(f'no getter registered: "{domain.key.version}"')
    if cached:
      cache_key = self._cache_key
      if not cache_key in factory_item.cache:
        value = clazz.get_value(filename, key, fallback = fallback, cached = False)
        factory_item.cache[cache_key] = value
      return factory_item.cache[cache_key]
#    filename, domain, group, name, version
    def _value_maker(f):
      return factory_item.getter.get_value(clazz, f)
    value = clazz.get_bytes(filename, key, _value_maker, fallback = fallback)
    if value == None:
      return None
    return factory_item.getter.decode_value(value)
'''

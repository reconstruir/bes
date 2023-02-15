#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.system.log import logger

from ..bfile_date import bfile_date
from ..bfile_check import bfile_check

from ..attributes.bfile_attr_mtime_cached import bfile_attr_mtime_cached
from ..attributes.bfile_attr_error import bfile_attr_error

from .bfile_metadata_factory_registry import bfile_metadata_factory_registry

class bfile_metadata(bfile_attr_mtime_cached):

  @classmethod
  def get_cached_metadata(clazz, filename, domain, group, name, version):
    filename = bfile_check.check_file(filename)
    clazz.check_part(domain)
    clazz.check_part(group)
    clazz.check_part(name)
    clazz.check_part(version)

    handler = bfile_metadata_factory_registry.get_handler(domain, group, name, version)
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

  @classmethod
  def check_part(clazz, part):
    clazz.check_key(part)
    
    if '/' in part:
      raise bfile_attr_error(f'"/" not supported in part: "{part}"')
  
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
'''

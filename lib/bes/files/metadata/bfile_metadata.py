#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.system.log import logger

from ..bfile_date import bfile_date
from ..bfile_check import bfile_check

from ..attr.bfile_attr_mtime_cached import bfile_attr_mtime_cached

from .bfile_metadata_error import bfile_metadata_error
from .bfile_metadata_factory_registry import bfile_metadata_factory_registry
from .bfile_metadata_key import bfile_metadata_key

class bfile_metadata(bfile_attr_mtime_cached):

  _log = logger('metadata')
  
  @classmethod
  def get_metadata(clazz, filename, key):
    filename = bfile_check.check_file(filename)
    key = check.check_bfile_metadata_key(key)
    handler = bfile_metadata_factory_registry.get_handler(key)
    assert handler.key == key
    item = clazz._get_item(filename, key)
    current_mtime = bfile_date.get_modification_date(filename)
    clazz._log.log_d(f'get_metadata: filename={filename} current_mtime={current_mtime} last_mtime={item._last_mtime}')
    if item._last_mtime != None:
      assert not item._last_mtime > current_mtime
      if current_mtime <= item._last_mtime:
        assert item._value != None
        return item._value
    if handler.getter:
      value_maker = lambda f__: handler.encode(handler.getter(f__))
    else:
      value_maker = None
    value_bytes, mtime, mtime_key, is_cached = clazz._do_get_cached_bytes(filename,
                                                                          key.as_string,
                                                                          value_maker)
    clazz._log.log_d(f'get_metadata: value_bytes={value_bytes} mtime={mtime} mtime_key={mtime_key} getter={handler.getter}')
    if not handler.getter:
      value_bytes = clazz.get_bytes(filename, key.as_string)
      if value_bytes == None:
        return None
      clazz.set_date(filename, mtime_key, mtime)
    value = handler.decoder(value_bytes)
    item._last_mtime = mtime
    item._value = value
    assert item._value != None
    item._count += 1
    assert item._value != None
    return item._value

  @classmethod
  def set_metadata(clazz, filename, key, value):
    filename = bfile_check.check_file(filename)
    key = check.check_bfile_metadata_key(key)
    handler = bfile_metadata_factory_registry.get_handler(key)
    assert handler.key == key
    item = clazz._get_item(filename, key)
    if handler.read_only:
      raise bfile_metadata_error(f'value is read only: "{key}"')
    assert handler.key == key
    encoded_value = handler.encode(value)
    if not check.is_bytes(encoded_value):
      raise bfile_metadata_error(f'encoded value should be bytes: "{encoded_value}" - {type(encoded_value)}')
    clazz.remove_mtime_key(filename, key.as_string)
    clazz.set_bytes(filename, key.as_string, encoded_value)
    item._last_mtime = None
    item._value = None
    #item._count += 1

  @classmethod
  def metadata_delete(clazz, filename, key):
    filename = bfile_check.check_file(filename)
    key = check.check_bfile_metadata_key(key)

    clazz.remove_mtime_key(filename, key.as_string)
    clazz.remove(filename, key.as_string)
    
  @classmethod
  def get_metadata_getter_count(clazz, filename, key):
    filename = bfile_check.check_file(filename)
    key = check.check_bfile_metadata_key(key)

    handler = bfile_metadata_factory_registry.get_handler(key)
    item = clazz._get_item(filename, handler.key)
    return item._count

  @classmethod
  def has_metadata(clazz, filename, key):
    filename = bfile_check.check_file(filename)
    key = check.check_bfile_metadata_key(key)

    return clazz.has_key(filename, key.as_string)
    
  _items = {}
  class _items_item(object):

    def __init__(self):
      self._last_mtime = None
      self._value = None
      self._count = 0

  @classmethod
  def _get_item(clazz, filename, key):
    if filename not in clazz._items:
      clazz._items[filename] = {}
    file_dict = clazz._items[filename]
    if not key in file_dict:
      file_dict[key] = clazz._items_item()
    return file_dict[key]

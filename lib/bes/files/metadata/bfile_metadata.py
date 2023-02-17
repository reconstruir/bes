#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.system.log import logger

from ..bfile_date import bfile_date
from ..bfile_check import bfile_check

from ..attributes.bfile_attr_mtime_cached import bfile_attr_mtime_cached

from .bfile_metadata_error import bfile_metadata_error
from .bfile_metadata_factory_registry import bfile_metadata_factory_registry
from .bfile_metadata_key import bfile_metadata_key

class bfile_metadata(bfile_attr_mtime_cached):

  @classmethod
  def get_metadata(clazz, filename, key):
    filename = bfile_check.check_file(filename)
    key = check.check_bfile_metadata_key(key)
    handler = bfile_metadata_factory_registry.get_handler(key)
    assert handler.key == key
    item = clazz._get_item(filename, handler.key)
    current_mtime = bfile_date.get_modification_date(filename)
    clazz._log.log_d(f'get_metadata: filename={filename} current_mtime={current_mtime} last_mtime={item._last_mtime}')
    if item._last_mtime != None:
      assert not item._last_mtime > current_mtime
      if current_mtime <= item._last_mtime:
        assert item._value != None
        return item._value
    value_bytes, mtime, _ = clazz._do_get_cached_bytes(filename, str(handler.key), handler.getter)
    value = handler.decoder(value_bytes)
    item._last_mtime = mtime
    item._value = value
    assert item._value != None
    item._count += 1
    assert item._value != None
    return item._value

  @classmethod
  def get_metadata_getter_count(clazz, filename, key):
    filename = bfile_check.check_file(filename)
    key = check.check_bfile_metadata_key(key)

    handler = bfile_metadata_factory_registry.get_handler(key)
    item = clazz._get_item(filename, handler.key)
    return item._count
  
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

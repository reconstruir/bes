#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.system.log import logger
from bes.property.cached_class_property import cached_class_property

from ..bf_date import bf_date
from ..bf_check import bf_check

from ..attr.bf_attr import bf_attr

from .bf_metadata_error import bf_metadata_error
from .bf_metadata_factory_registry import bf_metadata_factory_registry
from .bf_metadata_file_store import bf_metadata_file_store
from .bf_metadata_key import bf_metadata_key

class bf_metadata(object):

  _log = logger('metadata')

  @cached_class_property
  def _attr_instance(self):
    return bf_attr()

  _file_store_instance = None

  @classmethod
  def _get_file_store(clazz):
    if clazz._file_store_instance is None:
      clazz._file_store_instance = bf_metadata_file_store()
    return clazz._file_store_instance

  @classmethod
  def _set_file_store(clazz, store):
    clazz._file_store_instance = store

  @classmethod
  def set_int(clazz, filename, key, value, encoding = 'utf-8'):
    clazz._attr_instance.set_int(filename, key, value, encoding = encoding)

  @classmethod
  def get_int(clazz, filename, key):
    return clazz._attr_instance.get_int(filename, key)

  @classmethod
  def set_date(clazz, filename, key, value, encoding = 'utf-8'):
    clazz._attr_instance.set_date(filename, key, value, encoding = encoding)

  @classmethod
  def get_date(clazz, filename, key):
    return clazz._attr_instance.get_date(filename, key)

  @classmethod
  def get_cached_bytes_if_fresh(clazz, filename, key):
    return clazz._attr_instance.get_cached_bytes_if_fresh(filename, key)

  @classmethod
  def keys(clazz, filename, file_store = None):
    store = file_store if file_store is not None else clazz._get_file_store()
    return store.keys(filename)

  @classmethod
  def get_metadata(clazz, filename, key, file_store = None):
    filename = bf_check.check_file(filename)
    key = check.check_bf_metadata_key(key)
    desc = bf_metadata_factory_registry.get_description(key)
    clazz._log.log_d(f'get_metadata: desc={type(desc)}')
    assert desc.key == key
    store = file_store if file_store is not None else clazz._get_file_store()
    store_id = id(store) if file_store is not None else None
    item = clazz._get_item(filename, key, store_id)
    clazz._log.log_d(f'get_metadata: filename={filename} last_mtime={item._last_mtime}')
    if item._last_mtime is not None:
      current_mtime = bf_date.get_modification_date(filename)
      clazz._log.log_d(f'get_metadata: current_mtime={current_mtime}')
      if current_mtime <= item._last_mtime:
        clazz._log.log_d(f'get_metadata: returning cached value')
        return item._value

    stored = store.get(filename, key.as_string)
    if stored is not None:
      value_bytes = stored.encode('utf-8')
    else:
      value_bytes = None
      if desc.old_getter:
        old_bytes = clazz._find_old_value(filename, desc)
        if old_bytes is not None:
          check.check_bytes(old_bytes)
          value_bytes = old_bytes
      if value_bytes is None:
        value_bytes = desc.encode(desc.getter(filename))
      store.set(filename, key.as_string, value_bytes.decode('utf-8'))

    mtime = bf_date.get_modification_date(filename)
    clazz._log.log_d(f'get_metadata: value_bytes={value_bytes} mtime={mtime}')
    value = desc.decode(value_bytes)
    item._last_mtime = mtime
    item._value = value
    item._count += 1
    return item._value

  @classmethod
  def _find_old_value(clazz, filename, desc):
    clazz._log.log_d(f'_find_old_value: filename={filename}')
    assert desc.old_getter
    return desc.old_getter(filename)

  @classmethod
  def metadata_delete(clazz, filename, key, file_store = None):
    filename = bf_check.check_file(filename)
    key = check.check_bf_metadata_key(key)
    store = file_store if file_store is not None else clazz._get_file_store()
    store.delete(filename, key.as_string)
    clazz._attr_instance.remove_mtime_key(filename, key.as_string)
    if clazz._attr_instance.has_key(filename, key.as_string):
      clazz._attr_instance.remove(filename, key.as_string)

  @classmethod
  def get_metadata_getter_count(clazz, filename, key, file_store = None):
    filename = bf_check.check_file(filename)
    key = check.check_bf_metadata_key(key)
    desc = bf_metadata_factory_registry.get_description(key)
    store = file_store if file_store is not None else clazz._get_file_store()
    store_id = id(store) if file_store is not None else None
    item = clazz._get_item(filename, desc.key, store_id)
    return item._count

  @classmethod
  def has_metadata(clazz, filename, key, file_store = None):
    filename = bf_check.check_file(filename)
    key = check.check_bf_metadata_key(key)
    store = file_store if file_store is not None else clazz._get_file_store()
    return store.get(filename, key.as_string) is not None

  _items = {}
  class _items_item(object):

    def __init__(self):
      self._last_mtime = None
      self._value = None
      self._count = 0

  @classmethod
  def _get_item(clazz, filename, key, store_id):
    cache_key = (store_id, filename, key)
    if cache_key not in clazz._items:
      clazz._items[cache_key] = clazz._items_item()
    return clazz._items[cache_key]

#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.system.check import check
from bes.common.bool_util import bool_util
from bes.system.log import logger

from ..bf_check import bf_check
from ..bf_date import bf_date

from ._detail._bf_attr_getter_i import _bf_attr_getter_i

from .bf_attr_type_desc_datetime import bf_attr_type_desc_datetime
from .bf_attr_error import bf_attr_error
from .bf_attr_desc_registry import bf_attr_desc_registry

class bf_attr_getter_mixin:

  _log = logger('attr')
  
  @classmethod
  def check_key(clazz, key):
    check.check_string(key)

    for c in ( ' ', ':' ):
      if c in key:
        if c == ' ':
          label = 'space'
        else:
          label = c
        raise bf_attr_error(f'"{label}" not supported in key: "{key}"')
    return key

  def get_all(self, filename):
    'Return all attributes as a dictionary.'
    keys = self.keys(filename)
    result = {}
    for key in keys:
      result[key] = self.get_bytes(filename, key)
    return result

  def set_all(self, filename, attributes):
    'Set all file attributes.'
    for key, value in attributes.items():
      self.set_bytes(filename, key, value)

  def get_string(self, filename, key, encoding = 'utf-8'):
    'Return the attribute value with key for filename as string.'
    filename = bf_check.check_file(filename)
    key = self.check_key(key)
    value = self.get_bytes(filename, key)
    if value == None:
      return None
    return value.decode(encoding)

  def set_string(self, filename, key, value, encoding = 'utf-8'):
    'Set the value of attribute with key to value for filename as string.'
    filename = bf_check.check_file(filename)
    key = self.check_key(key)
    check.check_string(value)
    self.set_bytes(filename, key, value.encode(encoding))

  def get_date(self, filename, key):
    'Return the attribute value with key for filename as string.'
    filename = bf_check.check_file(filename)
    key = self.check_key(key)

    if not self.has_key(filename, key):
      return None
    value = self.get_bytes(filename, key)
    return bf_attr_type_desc_datetime.decode(value)

  def set_date(self, filename, key, value, encoding = 'utf-8'):
    'Set the value of attribute with key to value for filename as string.'
    filename = bf_check.check_file(filename)
    key = self.check_key(key)
    check.check_datetime(value)

    encoded_value = bf_attr_type_desc_datetime.encode(value)
    self.set_bytes(filename, key, encoded_value)

  def get_bool(self, filename, key):
    'Return the attribute value with key for filename as string.'
    filename = bf_check.check_file(filename)
    key = self.check_key(key)
    value = self.get_string(filename, key)
    if value == None:
      return None
    return bool_util.parse_bool(value)

  def set_bool(self, filename, key, value, encoding = 'utf-8'):
    'Set the value of attribute with key to value for filename as string.'
    filename = bf_check.check_file(filename)
    key = self.check_key(key)
    check.check_bool(value)
    
    self.set_string(filename, key, str(value).lower())
    
  def get_int(self, filename, key):
    'Return the attribute value with key for filename as string.'
    filename = bf_check.check_file(filename)
    key = self.check_key(key)
    
    value = self.get_string(filename, key)
    if value == None:
      return None
    return int(value)

  def set_int(self, filename, key, value, encoding = 'utf-8'):
    'Set the value of attribute with key to value for filename as string.'
    filename = bf_check.check_file(filename)
    key = self.check_key(key)
    check.check_int(value)
    
    self.set_string(filename, key, str(value))

  def get_float(self, filename, key):
    'Return the attribute value with key for filename as string.'
    filename = bf_check.check_file(filename)
    key = self.check_key(key)
    
    value = self.get_string(filename, key)
    if value == None:
      return None
    return float(value)

  def set_float(self, filename, key, value, encoding = 'utf-8'):
    'Set the value of attribute with key to value for filename as string.'
    filename = bf_check.check_file(filename)
    key = self.check_key(key)
    check.check_float(value)
    
    self.set_string(filename, key, str(value))

  def get_value(self, filename, key):
    filename = bf_check.check_file(filename)
    key = self.check_key(key)

    desc = bf_attr_desc_registry.get_value(key, raise_error = False)
    if not desc:
      raise bf_attr_error(f'No description registered for key: "{key}"')
      
    if self.has_key(filename, key):
      value_bytes = self.get_bytes(filename, key)
    else:
      if not desc.old_keys:
        return None
      value_bytes = None
      for old_key in desc.old_keys:
        if self.has_key(filename, old_key):
          value_bytes = self.get_bytes(filename, old_key)
          self.set_bytes(filename, key, value_bytes)
          break
    if value_bytes == None:
      return None
    return desc.decode(value_bytes)

  def set_value(self, filename, key, value):
    filename = bf_check.check_file(filename)
    key = self.check_key(key)

    desc = bf_attr_desc_registry.get_value(key, raise_error = False)
    if not desc:
      raise bf_attr_error(f'No description registered for key: "{key}"')
    
    if value == None:
      self.remove(key)
      
    checked_value = desc.check(value)
    encoded_value = desc.encode(checked_value)
    self.set_bytes(filename, key, encoded_value)

  def get_cached_bytes(self, filename, key, value_maker):
    'Return the attribute value with key for filename as bytes.'
    filename = bf_check.check_file(filename)
    key = self.check_key(key)
    check.check_callable(value_maker)

    value, _ = self._do_get_cached_bytes(filename, key, value_maker)
    return value

  @classmethod
  def make_mtime_key(clazz, key):
    return f'__bes_mtime_{key}__'

  _get_cached_bytes_result = namedtuple('_get_cached_bytes_result', 'value, mtime')
  def _do_get_cached_bytes(self, filename, key, value_maker):
    filename = bf_check.check_file(filename)
    key = self.check_key(key)
    check.check_callable(value_maker)

    self._log.log_method_d()

    mtime_key = self.make_mtime_key(key)
    attr_mtime = self.get_date(filename, mtime_key)
    file_mtime = bf_date.get_modification_date(filename)
    value = None
    
    label = f'_do_get_cached_bytes:{filename}:{key}'

    self._log.log_d(f'{label}: attr_mtime={attr_mtime} file_mtime={file_mtime}')
    
    if file_mtime == attr_mtime:
      value = self.get_bytes(filename, key)
      self._log.log_d(f'{label}: 1: value={value}')
      return self._get_cached_bytes_result(value, file_mtime)

    value = value_maker(filename)
    if value == None:
      raise bf_attr_error(f'value should never be None')

    self._log.log_d(f'{label}: 3: value={value}')
    self.set_bytes(filename, key, value)
    file_mtime = bf_date.get_modification_date(filename)
    self._log.log_d(f'{label}: 3: file_mtime={file_mtime}')
    self.set_date(filename, mtime_key, file_mtime)
    # setting the date in the line above has the side effect
    # of changing the mtime in some implementations.  so we
    # force it to be what it was right after setting the value
    # which is in the past (usually microseconds) but guaranteed
    # to match what what was set in set_date()
    bf_date.set_modification_date(filename, file_mtime)
    return self._get_cached_bytes_result(value, file_mtime)

  def remove_mtime_key(self, filename, key):
    'Remove the mtime key for key.'
    filename = bf_check.check_file(filename)
    key = self.check_key(key)
    mtime_key = self.make_mtime_key(key)

    if self.has_key(filename, mtime_key):
      self.remove(filename, mtime_key)

  def get_cached_bytes_if_fresh(self, filename, key):
    'Return the mtime cached bytes but only if they are fresh.  Otherwise return None.'
    if not self.has_key(filename, key):
      return None
    mtime_key = self.make_mtime_key(key)
    if not self.has_key(filename, mtime_key):
      return None
    attr_mtime = self.get_date(filename, mtime_key)
    file_mtime = bf_date.get_modification_date(filename)
    self._log.log_d(f'get_cached_bytes_if_fresh: key={key} mtime_key={mtime_key} attr_mtime={attr_mtime} file_mtime={file_mtime}')
    if file_mtime == attr_mtime:
      return self.get_bytes(filename, key)
    return None

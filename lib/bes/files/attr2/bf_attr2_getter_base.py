#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.system.check import check
from bes.common.bool_util import bool_util
from bes.system.log import logger

from ..bf_check import bf_check
from ..bf_date import bf_date

from ._detail._bf_attr2_getter_super_class import _bf_attr2_getter_super_class
from ._detail._bf_attr2_getter_i import _bf_attr2_getter_i

from .bf_attr2_type_desc_datetime import bf_attr2_type_desc_datetime
from .bf_attr2_error import bf_attr2_error
from .bf_attr2_desc_registry import bf_attr2_desc_registry

#from ._detail._bf_attr2_getter_super_class import _bf_attr2_getter_super_class

class bf_attr2_getter_base(_bf_attr2_getter_super_class):

  _log = logger('attr')
  
  def __init__(self, impl):
    assert isinstance(impl, _bf_attr2_getter_i)
    self._impl = impl

  @classmethod
  def check_key(clazz, key):
    check.check_string(key)

    for c in ( ' ', ':' ):
      if c in key:
        if c == ' ':
          label = 'space'
        else:
          label = c
        raise bf_attr2_error(f'"{label}" not supported in key: "{key}"')
    return key

  @classmethod
  def get_all(clazz, filename):
    'Return all attributes as a dictionary.'
    keys = clazz.keys(filename)
    result = {}
    for key in keys:
      result[key] = clazz.get_bytes(filename, key)
    return result

  @classmethod
  def set_all(clazz, filename, attributes):
    'Set all file attributes.'
    for key, value in attributes.items():
      clazz.set_bytes(filename, key, value)

  @classmethod
  def get_string(clazz, filename, key, encoding = 'utf-8'):
    'Return the attribute value with key for filename as string.'
    filename = bf_check.check_file(filename)
    key = clazz.check_key(key)
    value = clazz.get_bytes(filename, key)
    if value == None:
      return None
    return value.decode(encoding)

  @classmethod
  def set_string(clazz, filename, key, value, encoding = 'utf-8'):
    'Set the value of attribute with key to value for filename as string.'
    filename = bf_check.check_file(filename)
    key = clazz.check_key(key)
    check.check_string(value)
    clazz.set_bytes(filename, key, value.encode(encoding))

  @classmethod
  def get_date(clazz, filename, key):
    'Return the attribute value with key for filename as string.'
    filename = bf_check.check_file(filename)
    key = clazz.check_key(key)

    if not clazz.has_key(filename, key):
      return None
    value = clazz.get_bytes(filename, key)
    return bf_attr2_type_desc_datetime.decode(value)

  @classmethod
  def set_date(clazz, filename, key, value, encoding = 'utf-8'):
    'Set the value of attribute with key to value for filename as string.'
    filename = bf_check.check_file(filename)
    key = clazz.check_key(key)
    check.check_datetime(value)

    encoded_value = bf_attr2_type_desc_datetime.encode(value)
    clazz.set_bytes(filename, key, encoded_value)

  @classmethod
  def get_bool(clazz, filename, key):
    'Return the attribute value with key for filename as string.'
    filename = bf_check.check_file(filename)
    key = clazz.check_key(key)
    value = clazz.get_string(filename, key)
    if value == None:
      return None
    return bool_util.parse_bool(value)

  @classmethod
  def set_bool(clazz, filename, key, value, encoding = 'utf-8'):
    'Set the value of attribute with key to value for filename as string.'
    filename = bf_check.check_file(filename)
    key = clazz.check_key(key)
    check.check_bool(value)
    
    clazz.set_string(filename, key, str(value).lower())
    
  @classmethod
  def get_int(clazz, filename, key):
    'Return the attribute value with key for filename as string.'
    filename = bf_check.check_file(filename)
    key = clazz.check_key(key)
    
    value = clazz.get_string(filename, key)
    if value == None:
      return None
    return int(value)

  @classmethod
  def set_int(clazz, filename, key, value, encoding = 'utf-8'):
    'Set the value of attribute with key to value for filename as string.'
    filename = bf_check.check_file(filename)
    key = clazz.check_key(key)
    check.check_int(value)
    
    clazz.set_string(filename, key, str(value))

  @classmethod
  def get_float(clazz, filename, key):
    'Return the attribute value with key for filename as string.'
    filename = bf_check.check_file(filename)
    key = clazz.check_key(key)
    
    value = clazz.get_string(filename, key)
    if value == None:
      return None
    return float(value)

  @classmethod
  def set_float(clazz, filename, key, value, encoding = 'utf-8'):
    'Set the value of attribute with key to value for filename as string.'
    filename = bf_check.check_file(filename)
    key = clazz.check_key(key)
    check.check_float(value)
    
    clazz.set_string(filename, key, str(value))

  @classmethod
  def get_value(clazz, filename, key):
    filename = bf_check.check_file(filename)
    key = clazz.check_key(key)

    desc = bf_attr2_desc_registry.get_value(key, raise_error = False)
    if not desc:
      raise bf_attr2_error(f'No description registered for key: "{key}"')
      
    if clazz.has_key(filename, key):
      value_bytes = clazz.get_bytes(filename, key)
    else:
      if not desc.old_keys:
        return None
      value_bytes = None
      for old_key in desc.old_keys:
        if clazz.has_key(filename, old_key):
          value_bytes = clazz.get_bytes(filename, old_key)
          clazz.set_bytes(filename, key, value_bytes)
          break
    if value_bytes == None:
      return None
    return desc.decode(value_bytes)

  @classmethod
  def set_value(clazz, filename, key, value):
    filename = bf_check.check_file(filename)
    key = clazz.check_key(key)

    desc = bf_attr2_desc_registry.get_value(key, raise_error = False)
    if not desc:
      raise bf_attr2_error(f'No description registered for key: "{key}"')
    
    if value == None:
      clazz.remove(key)
      
    checked_value = desc.check(value)
    encoded_value = desc.encode(checked_value)
    clazz.set_bytes(filename, key, encoded_value)

  @classmethod
  def get_cached_bytes(clazz, filename, key, value_maker):
    'Return the attribute value with key for filename as bytes.'
    filename = bf_check.check_file(filename)
    key = clazz.check_key(key)
    check.check_callable(value_maker)

    value, _ = clazz._do_get_cached_bytes(filename, key, value_maker)
    return value

  @classmethod
  def make_mtime_key(clazz, key):
    return f'__bes_mtime_{key}__'

  _get_cached_bytes_result = namedtuple('_get_cached_bytes_result', 'value, mtime')
  @classmethod
  def _do_get_cached_bytes(clazz, filename, key, value_maker):
    filename = bf_check.check_file(filename)
    key = clazz.check_key(key)
    check.check_callable(value_maker)

    clazz._log.log_method_d()

    mtime_key = clazz.make_mtime_key(key)
    attr_mtime = clazz.get_date(filename, mtime_key)
    file_mtime = bf_date.get_modification_date(filename)
    value = None
    
    label = f'_do_get_cached_bytes:{filename}:{key}'

    clazz._log.log_d(f'{label}: attr_mtime={attr_mtime} file_mtime={file_mtime}')
    
    if file_mtime == attr_mtime:
      value = clazz.get_bytes(filename, key)
      clazz._log.log_d(f'{label}: 1: value={value}')
      return clazz._get_cached_bytes_result(value, file_mtime)

    value = value_maker(filename)
    if value == None:
      raise bf_attr2_error(f'value should never be None')

    clazz._log.log_d(f'{label}: 3: value={value}')
    clazz.set_bytes(filename, key, value)
    file_mtime = bf_date.get_modification_date(filename)
    clazz._log.log_d(f'{label}: 3: file_mtime={file_mtime}')
    clazz.set_date(filename, mtime_key, file_mtime)
    # setting the date in the line above has the side effect
    # of changing the mtime in some implementations.  so we
    # force it to be what it was right after setting the value
    # which is in the past (usually microseconds) but guaranteed
    # to match what what was set in set_date()
    bf_date.set_modification_date(filename, file_mtime)
    return clazz._get_cached_bytes_result(value, file_mtime)

  @classmethod
  def remove_mtime_key(clazz, filename, key):
    'Remove the mtime key for key.'
    filename = bf_check.check_file(filename)
    key = clazz.check_key(key)
    mtime_key = clazz.make_mtime_key(key)

    if clazz.has_key(filename, mtime_key):
      clazz.remove(filename, mtime_key)

  @classmethod
  def get_cached_bytes_if_fresh(clazz, filename, key):
    'Return the mtime cached bytes but only if they are fresh.  Otherwise return None.'
    if not clazz.has_key(filename, key):
      return None
    mtime_key = clazz.make_mtime_key(key)
    if not clazz.has_key(filename, mtime_key):
      return None
    attr_mtime = clazz.get_date(filename, mtime_key)
    file_mtime = bf_date.get_modification_date(filename)
    clazz._log.log_d(f'get_cached_bytes_if_fresh: key={key} mtime_key={mtime_key} attr_mtime={attr_mtime} file_mtime={file_mtime}')
    if file_mtime == attr_mtime:
      return clazz.get_bytes(filename, key)
    return None
      
#class bf_attr2(_bf_attr2_getter_super_class, _bf_attr2_mixin):
#  pass

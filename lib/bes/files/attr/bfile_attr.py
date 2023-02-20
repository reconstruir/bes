#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.common.bool_util import bool_util
from bes.system.log import logger
from bes.files.bfile_check import bfile_check

from ..bfile_date import bfile_date

from ._detail._bfile_attr_super_class import _bfile_attr_super_class

from .bfile_attr_encoding import bfile_attr_encoding
from .bfile_attr_error import bfile_attr_error
from .bfile_attr_value_registry import bfile_attr_value_registry

class _bfile_attr_mixin:

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
        raise bfile_attr_error(f'"{label}" not supported in key: "{key}"')
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
    filename = bfile_check.check_file(filename)
    key = clazz.check_key(key)
    value = clazz.get_bytes(filename, key)
    if value == None:
      return None
    return value.decode(encoding)

  @classmethod
  def set_string(clazz, filename, key, value, encoding = 'utf-8'):
    'Set the value of attribute with key to value for filename as string.'
    filename = bfile_check.check_file(filename)
    key = clazz.check_key(key)
    check.check_string(value)
    clazz.set_bytes(filename, key, value.encode(encoding))

  @classmethod
  def get_date(clazz, filename, key):
    'Return the attribute value with key for filename as string.'
    filename = bfile_check.check_file(filename)
    key = clazz.check_key(key)

    if not clazz.has_key(filename, key):
      return None
    value = clazz.get_bytes(filename, key)
    return bfile_attr_encoding.decode_datetime(value)

  @classmethod
  def set_date(clazz, filename, key, value, encoding = 'utf-8'):
    'Set the value of attribute with key to value for filename as string.'
    filename = bfile_check.check_file(filename)
    key = clazz.check_key(key)
    check.check_datetime(value)

    encoded_value = bfile_attr_encoding.encode_datetime(value)
    clazz.set_bytes(filename, key, encoded_value)

  @classmethod
  def get_bool(clazz, filename, key):
    'Return the attribute value with key for filename as string.'
    filename = bfile_check.check_file(filename)
    key = clazz.check_key(key)
    value = clazz.get_string(filename, key)
    if value == None:
      return None
    return bool_util.parse_bool(value)

  @classmethod
  def set_bool(clazz, filename, key, value, encoding = 'utf-8'):
    'Set the value of attribute with key to value for filename as string.'
    filename = bfile_check.check_file(filename)
    key = clazz.check_key(key)
    check.check_bool(value)
    
    clazz.set_string(filename, key, str(value).lower())
    
  @classmethod
  def get_int(clazz, filename, key):
    'Return the attribute value with key for filename as string.'
    filename = bfile_check.check_file(filename)
    key = clazz.check_key(key)
    
    value = clazz.get_string(filename, key)
    if value == None:
      return None
    return int(value)

  @classmethod
  def set_int(clazz, filename, key, value, encoding = 'utf-8'):
    'Set the value of attribute with key to value for filename as string.'
    filename = bfile_check.check_file(filename)
    key = clazz.check_key(key)
    check.check_int(value)
    
    clazz.set_string(filename, key, str(value))

  @classmethod
  def get_float(clazz, filename, key):
    'Return the attribute value with key for filename as string.'
    filename = bfile_check.check_file(filename)
    key = clazz.check_key(key)
    
    value = clazz.get_string(filename, key)
    if value == None:
      return None
    return float(value)

  @classmethod
  def set_float(clazz, filename, key, value, encoding = 'utf-8'):
    'Set the value of attribute with key to value for filename as string.'
    filename = bfile_check.check_file(filename)
    key = clazz.check_key(key)
    check.check_float(value)
    
    clazz.set_string(filename, key, str(value))

  @classmethod
  def get_value(clazz, filename, key):
    filename = bfile_check.check_file(filename)
    key = clazz.check_key(key)

    handler = bfile_attr_value_registry.get_handler(key, raise_error = False)
    if not handler:
      raise bfile_attr_error(f'No value registered: "{key}"')
      
    if not clazz.has_key(filename, key):
      return None

    value_bytes = clazz.get_bytes(filename, key)
    return handler.decode(value_bytes)

  @classmethod
  def set_value(clazz, filename, key, value):
    filename = bfile_check.check_file(filename)
    key = clazz.check_key(key)

    handler = bfile_attr_value_registry.get_handler(key, raise_error = False)
    if not handler:
      raise bfile_attr_error(f'No value registered: "{key}"')
    
    if value == None:
      clazz.remove(key)
      
    checked_value = handler.check(value)
    encoded_value = handler.encode(checked_value)
    clazz.set_bytes(filename, key, encoded_value)
  
class bfile_attr(_bfile_attr_super_class, _bfile_attr_mixin):
  pass

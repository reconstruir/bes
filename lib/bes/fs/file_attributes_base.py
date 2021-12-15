#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from datetime import datetime

from abc import abstractmethod, ABCMeta
from bes.system.compat import with_metaclass

from bes.common.check import check
from bes.fs.file_check import file_check

class file_attributes_base(with_metaclass(ABCMeta, object)):

  @classmethod
  @abstractmethod
  def has_key(clazz, filename, key):
    'Return True if filename has an attributed with key.'
    raise NotImplemented('has_key')
  
  @classmethod
  @abstractmethod
  def get_bytes(clazz, filename, key):
    'Return the attribute value with key for filename as bytes.'
    raise NotImplemented('get_bytes')

  @classmethod
  @abstractmethod
  def set_bytes(clazz, filename, key, value):
    'Set the value of attribute with key to value for filename as bytes.'
    raise NotImplemented('set_bytes')
  
  @classmethod
  @abstractmethod
  def remove(clazz, filename, key):
    'Remove the attirbute with key from filename.'
    raise NotImplemented('remove')
  
  @classmethod
  @abstractmethod
  def keys(clazz, filename):
    'Return all the keys set for filename.'
    raise NotImplemented('keys')

  @classmethod
  @abstractmethod
  def clear(clazz, filename):
    'Create all attributes.'
    raise NotImplemented('clear')

  @classmethod
  def _check_key(clazz, key):
    check.check_string(key)
    if ' ' in key:
      raise ValueError('space not supported in key: \"{}\"'.format(key))
    if ':' in key:
      raise ValueError('colon not supported in key: \"{}\"'.format(key))
    return key

  @classmethod
  def get_all(clazz, filename):
    'Return all attributes as a dictionary.'
    keys = clazz.keys(filename)
    result = {}
    for key in keys:
      result[key] = clazz.get(filename, key)
    return result

  @classmethod
  def set_all(clazz, filename, attributes):
    'Set all file attributes.'
    for key, value in attributes.items():
      clazz.set(filename, key, value)

  @classmethod
  @abstractmethod
  def get_string(clazz, filename, key, encoding = 'utf-8'):
    'Return the attribute value with key for filename as string.'
    filename = file_check.check_file(filename)
    key = clazz._check_key(key)
    value = clazz.get_bytes(filename, key)
    if value == None:
      return None
    return value.decode(encoding)

  @classmethod
  @abstractmethod
  def set_string(clazz, filename, key, value, encoding = 'utf-8'):
    'Set the value of attribute with key to value for filename as string.'
    filename = file_check.check_file(filename)
    key = clazz._check_key(key)
    check.check_string(value)
    clazz.set_bytes(filename, key, value.encode(encoding))

  @classmethod
  @abstractmethod
  def get_date(clazz, filename, key):
    'Return the attribute value with key for filename as string.'
    filename = file_check.check_file(filename)
    key = clazz._check_key(key)
    value = clazz.get_string(filename, key)
    if value == None:
      return None
    timestamp = float(value)
    return datetime.fromtimestamp(timestamp)

  @classmethod
  @abstractmethod
  def set_date(clazz, filename, key, value, encoding = 'utf-8'):
    'Set the value of attribute with key to value for filename as string.'
    filename = file_check.check_file(filename)
    key = clazz._check_key(key)
    check.check(value, datetime)
    
    clazz.set_string(filename, key, str(value.timestamp()))

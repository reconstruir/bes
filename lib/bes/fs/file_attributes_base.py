#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os

from datetime import datetime

from abc import abstractmethod, ABCMeta

from ..system.check import check
from bes.common.bool_util import bool_util
from bes.fs.file_check import file_check

from .file_attributes_error import file_attributes_permission_error

class file_attributes_base(object, metaclass = ABCMeta):

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
    filename = file_check.check_file(filename)
    key = clazz._check_key(key)
    value = clazz.get_bytes(filename, key)
    if value == None:
      return None
    return value.decode(encoding)

  @classmethod
  def set_string(clazz, filename, key, value, encoding = 'utf-8'):
    'Set the value of attribute with key to value for filename as string.'
    filename = file_check.check_file(filename)
    key = clazz._check_key(key)
    check.check_string(value)
    clazz.set_bytes(filename, key, value.encode(encoding))

  @classmethod
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
  def set_date(clazz, filename, key, value, encoding = 'utf-8'):
    'Set the value of attribute with key to value for filename as string.'
    filename = file_check.check_file(filename)
    key = clazz._check_key(key)
    check.check(value, datetime)
    
    clazz.set_string(filename, key, str(value.timestamp()))

  @classmethod
  def get_bool(clazz, filename, key):
    'Return the attribute value with key for filename as string.'
    filename = file_check.check_file(filename)
    key = clazz._check_key(key)
    value = clazz.get_string(filename, key)
    if value == None:
      return None
    return bool_util.parse_bool(value)

  @classmethod
  def set_bool(clazz, filename, key, value, encoding = 'utf-8'):
    'Set the value of attribute with key to value for filename as string.'
    filename = file_check.check_file(filename)
    key = clazz._check_key(key)
    check.check_bool(value)
    
    clazz.set_string(filename, key, str(value).lower())
    
  @classmethod
  def get_int(clazz, filename, key):
    'Return the attribute value with key for filename as string.'
    filename = file_check.check_file(filename)
    key = clazz._check_key(key)
    
    value = clazz.get_string(filename, key)
    if value == None:
      return None
    return int(value)

  @classmethod
  def set_int(clazz, filename, key, value, encoding = 'utf-8'):
    'Set the value of attribute with key to value for filename as string.'
    filename = file_check.check_file(filename)
    key = clazz._check_key(key)
    check.check_int(value)
    
    clazz.set_string(filename, key, str(value))
    
  @classmethod
  def check_file_is_readable(clazz, filename):
    'Check that filename is readable and raise a permission error if not.'
    filename = file_check.check_file(filename)

    if not os.access(filename, os.R_OK):
      raise file_attributes_permission_error('File is not readable: {}'.format(filename))

  @classmethod
  def check_file_is_writable(clazz, filename):
    'Check that filename is writable and raise a permission error if not.'
    filename = file_check.check_file(filename)

    if not os.access(filename, os.W_OK):
      raise file_attributes_permission_error('File is not writable: {}'.format(filename))
      

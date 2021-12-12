#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta
from bes.system.compat import with_metaclass

from bes.common.check import check

class file_attributes_base(with_metaclass(ABCMeta, object)):

  @classmethod
  @abstractmethod
  def has_key(clazz, filename, key):
    'Return True if filename has an attributed with key.'
    raise NotImplemented('has_key')
  
  @classmethod
  @abstractmethod
  def get(clazz, filename, key):
    'Return the attribute value with key for filename.'
    raise NotImplemented('get')

  @classmethod
  @abstractmethod
  def set(clazz, filename, key, value):
    'Set the value of attribute with key to value for filename.'
    raise NotImplemented('set')
  
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

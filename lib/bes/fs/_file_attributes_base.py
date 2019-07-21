#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

#import os.path as path
from abc import abstractmethod, ABCMeta
from bes.system.compat import with_metaclass

class _file_attributes_base(with_metaclass(ABCMeta, object)):

  @classmethod
  @abstractmethod
  def get(clazz, filename, key):
    'Return the attribute value with key for filename.'
    pass

  @classmethod
  @abstractmethod
  def set(clazz, filename, key, value):
    'Set the value of attribute with key to value for filename.'
    pass
  
  @classmethod
  @abstractmethod
  def remove(clazz, filename, key):
    'Remove the attirbute with key from filename.'
    pass
  
  @classmethod
  @abstractmethod
  def keys(clazz, filename):
    'Return all the keys set for filename.'
    pass

  @classmethod
  @abstractmethod
  def clear(clazz, filename):
    'Create all attributes.'
    pass

  @classmethod
  def _check_key(clazz, key):
    if ' ' in key:
      raise ValueError('space not supported in key: \"{}\"'.format(key))

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

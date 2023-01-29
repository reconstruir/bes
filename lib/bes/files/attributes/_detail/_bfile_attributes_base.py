#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta
from bes.system.compat import with_metaclass

class _bfile_attributes_base(with_metaclass(ABCMeta, object)):

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

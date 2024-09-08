#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta
from bes.system.compat import with_metaclass

class _bf_attr_getter_i(with_metaclass(ABCMeta, object)):

  @abstractmethod
  def has_key(self, filename, key):
    'Return True if filename has an attributed with key.'
    raise NotImplementedError('has_key')
  
  @abstractmethod
  def get_bytes(self, filename, key):
    'Return the attribute value with key for filename as bytes.'
    raise NotImplementedError('get_bytes')

  @abstractmethod
  def set_bytes(self, filename, key, value):
    'Set the value of attribute with key to value for filename as bytes.'
    raise NotImplementedError('set_bytes')
  
  @abstractmethod
  def remove(self, filename, key):
    'Remove the attirbute with key from filename.'
    raise NotImplementedError('remove')
  
  @abstractmethod
  def keys(self, filename):
    'Return all the keys set for filename.'
    raise NotImplementedError('keys')

  @abstractmethod
  def clear(self, filename):
    'Create all attributes.'
    raise NotImplementedError('clear')

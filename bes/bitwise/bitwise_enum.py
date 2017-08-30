#!/usr/bin/env python
#-*- coding:utf-8 -*-

import inspect
from bitwise_unpack import bitwise_unpack

class _bitwise_enum_meta(type):

  def __new__(meta, name, bases, class_dict):
    clazz = type.__new__(meta, name, bases, class_dict)
    if clazz.__name__ != 'bitwise_enum':
      size = getattr(clazz, 'SIZE', 1)
      if size not in [ 1, 2, 4, 8 ]:
        raise TypeError('Invalid SIZE.  Should be 1, 2, 4 or 8: %s' % (size))

      names = [ f for f in clazz.__dict__ if not f.startswith('_') ]
      names = [ f for f in names if f not in [ 'SIZE', 'DEFAULT' ] ]
      values = [ getattr(clazz, name) for name in names ]

      for value in values:
        if not isinstance(value, int):
          raise TypeError('Value should be of type int instead of %s: %s' % (type(value), str(value)))
      
      setattr(clazz, '_NAMES', sorted(names))
      setattr(clazz, '_VALUES', sorted(values))
      
      dvalues = {}
      min_value = None
      for name in names:
        value = getattr(clazz, name)
        dvalues[name] = getattr(clazz, name)
        if min_value is None:
          min_value = value
        else:
          min_value = min(min_value, value)
          
      setattr(clazz, '_DVALUES', dvalues)

      if not hasattr(clazz, 'DEFAULT'):
        setattr(clazz, 'DEFAULT', min_value)
      default = getattr(clazz, 'DEFAULT')
      if not isinstance(default, int):
        raise TypeError('DEFAULT should be of type int instead of %s: %s' % (type(default), str(default)))
      if not default in values:
        raise ValueError('DEFAULT invalid: %d' % (default))
      
    return clazz

class bitwise_enum(object):

  __metaclass__ = _bitwise_enum_meta

  def __init__(self, value = None):
    if value is None:
      value = self.DEFAULT
    self._value = value

  @classmethod
  def value_is_valid(clazz, value):
    return value in clazz._VALUES

  @classmethod
  def name_is_valid(clazz, name):
    return name in clazz._NAMES

  @property
  def value(self):
    return self._value

  @value.setter
  def value(self, value):
    if not self.value_is_valid(value):
      raise ValueError('Invalid value \"%s\".  Should be one of %s' % (value, ' '.join(self._VALUES)))
    self._value = value
  
  @classmethod
  def parse(clazz, s):
    if not s in clazz._NAMES:
      return None
    return self._DVALUES[s]
  
  def write_to_io(self, io):
    pass
    
  def read_from_io(self):
    pass
    #self._assert size in [ 1, 2, 4, 8]
    #return bitwise_unpack.unpack(self._stream.read(size), size, endian = self._endian)

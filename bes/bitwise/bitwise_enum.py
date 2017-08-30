#!/usr/bin/env python
#-*- coding:utf-8 -*-

import inspect
from bitwise_unpack import bitwise_unpack

class _bitwise_enum_meta(type):
  'Cheesy enum.  Id rather use the one in python3 but i want to support python 2.7 with no exta deps.'
  
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

      names_values = zip(names, values)
      setattr(clazz, '_NAME_VALUES', sorted(names_values))
      setattr(clazz, '_NAMES', sorted(names))
      setattr(clazz, '_VALUES', sorted(values))
      
      name_to_value = {}
      min_value = None
      value_to_name = {}
      for name in names:
        value = getattr(clazz, name)
        name_to_value[name] = getattr(clazz, name)
        if min_value is None:
          min_value = value
        else:
          min_value = min(min_value, value)
        if not value_to_name.has_key(value):
          value_to_name[value] = []
        value_to_name[value].append(name)
          
      setattr(clazz, '_NAME_TO_VALUE', name_to_value)
      setattr(clazz, '_VALUE_TO_NAME', value_to_name)

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

  def __str__(self):
    return self._VALUE_TO_NAME[self._value][0]
    
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
      choices = ' '.join([ '%s(%s)' % (name, value) for name, value in self._NAME_VALUES ])
      raise ValueError('Invalid value: %s - should be one of %s' % (value, choices))
    self._value = value
  
  @classmethod
  def parse(clazz, s):
    if not s in clazz._NAMES:
      return None
    return self._NAME_TO_VALUE[s]
  
  def write_to_io(self, io):
    io.write(self._value, self.SIZE)
    
  def read_from_io(self):
    self.value = io.read(self.SIZE)

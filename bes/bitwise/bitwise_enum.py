#!/usr/bin/env python
#-*- coding:utf-8 -*-

from bes.common import enum

class _enum_loader(object):

  @staticmethod
  def load_size(target):
    return getattr(target, 'SIZE', 1)

  @staticmethod
  def load_default_value(target):
    return getattr(target, 'DEFAULT', None)

  @staticmethod
  def size_is_valid(size):
    return size in [ 1, 2, 4, 8 ]
  
  @staticmethod
  def load_name_values(target):
    names = [ f for f in target.__dict__ if not f.startswith('_') ]
    names = [ f for f in names if f not in [ 'SIZE', 'DEFAULT' ] ]
    values = [ getattr(target, name) for name in names ]
    assert len(names) == len(values)
    return zip(names, values)

  
class _bitwise_enum_meta(type):
  'Cheesy enum.  Id rather use the one in python3 but i want to support python 2.7 with no exta deps.'
  
  def __new__(meta, name, bases, class_dict):
    clazz = type.__new__(meta, name, bases, class_dict)
    if clazz.__name__ != 'bitwise_enum':
      size = _enum_loader.load_size(clazz)
      if not _enum_loader.size_is_valid(size):
        raise TypeError('Invalid SIZE.  Should be 1, 2, 4 or 8 instead of: %s' % (size))

      name_values = _enum_loader.load_name_values(clazz)
      for name, value in name_values:
        if not isinstance(value, int):
          raise TypeError('Value should be of type int instead of %s: %s' % (type(value), str(value)))

      setattr(clazz, '_NAME_VALUES', sorted(name_values))
      setattr(clazz, '_NAMES', sorted([ x[0] for x in name_values]))
      setattr(clazz, '_VALUES', sorted([ x[1] for x in name_values]))
      
      name_to_value = {}
      min_value = None
      value_to_name = {}
      for name, value in name_values:
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
      if not default in [ x[1] for x in name_values]:
        raise ValueError('DEFAULT invalid: %d' % (default))
      
    return clazz

class bitwise_enum(object):

  __metaclass__ = _bitwise_enum_meta

  def __init__(self, value = None):
    if value is None:
      value = self.DEFAULT
    self.assign(value)

  def __str__(self):
    return self._VALUE_TO_NAME[self._value][0]
    
  @classmethod
  def value_is_valid(clazz, value):
    return value in clazz._VALUES

  @classmethod
  def name_is_valid(clazz, name):
    return name in clazz._NAMES

  def assign(self, something):
    if isinstance(something, self.__class__):
      self.value = something.value
    elif isinstance(something, ( str, unicode )):
      self.value = self.parse(something)
    elif isinstance(something, int):
      self.value = something
    else:
      raise ValueError('invalid value: %s' % (str(something)))
  
  @property
  def value(self):
    return self._value

  @value.setter
  def value(self, value):
    if not self.value_is_valid(value):
      raise ValueError('Invalid value: %s - should be one of %s' % (value, self._make_choices_blurb()))
    self._value = value

  @property
  def name(self):
    return self._VALUE_TO_NAME[self._value][0]

  @name.setter
  def name(self, name):
    if not self.name_is_valid(name):
      raise ValueError('Invalid name: %s - should be one of %s' % (name, self._make_choices_blurb()))
    self.value = self._NAME_TO_VALUE[name]

  @classmethod
  def _make_choices_blurb(clazz):
    return ' '.join([ '%s(%s)' % (name, value) for name, value in clazz._NAME_VALUES ])
    
  @classmethod
  def parse(clazz, s):
    if not isinstance(s, ( str, unicode )):
      raise TypeError('Value to parse should be a string instead of: %s - %s' % (str(s), type(s)))
    if not s in clazz._NAMES:
      raise ValueError('Value invalid: %s' % (str(s)))
    return clazz._NAME_TO_VALUE[s]
  
  def write_to_io(self, io):
    io.write(self._value, self.SIZE)
    
  def read_from_io(self, io):
    self.value = io.read(self.SIZE)

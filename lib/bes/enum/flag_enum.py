#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .enum_loader import enum_loader

class _flag_enum_meta_class(type):
  'cheesy enum.  Id rather use the one in python3 but i want to support python 2.7 with no exta deps.'
  
  def __new__(meta, name, bases, class_dict):
    clazz = type.__new__(meta, name, bases, class_dict)
    if hasattr(clazz, '_ENUM'):
      raise RuntimeError('subclassing %s not allowed.' % (bases[-1]))
    e = enum_loader.load(clazz)
    if e:
      clazz._ENUM = e
      masks = []
      for i in range(0, clazz.SIZE * 8):
        masks.append(0x1 << i)
      setattr(clazz, 'MASKS', masks)
    return clazz

class flag_enum(object):

  DELIMITER = '|'
  
  __metaclass__ = _flag_enum_meta_class

  def __init__(self, value = 0):
    self.assign(value)

  def matches(self, mask):
    return (self.value & mask) != 0
    
  def __str__(self):
    v = []
    for n in self._ENUM.name_values:
      if n.value in self.MASKS:
        if self.matches(n.value):
          v.append(n.name)
    return self.DELIMITER.join(sorted(v))
    
  def __eq__(self, other):
    if isinstance(other, self.__class__):
      return self.value == other.value
    elif isinstance(other, basestring):
      return self.value == self.parse(other)
    elif isinstance(other, int):
      return self.value == other
    else:
      raise TypeError('invalid other: %s - %s' % (str(other), type(other)))
    
  @classmethod
  def value_is_valid(clazz, value):
    return self._ENUM.value_is_valid(value)

  @classmethod
  def name_is_valid(clazz, name):
    return self._ENUM.name_is_valid(name)

  def assign(self, what):
    if isinstance(what, self.__class__):
      self.value = what.value
    elif isinstance(what, basestring):
      self.value = self.parse(what)
    elif isinstance(what, int):
      self.value = what
    else:
      raise TypeError('invalid value: %s' % (str(what)))
  
  @property
  def value(self):
    return self._value

  @value.setter
  def value(self, value):
    assert isinstance(value, int)
    self._value = value

  @property
  def name(self):
    return self._ENUM.value_to_name(self._value)

  @name.setter
  def name(self, name):
    self._ENUM.check_name(name)
    self.value = self._ENUM.name_to_value(name)
  
  @classmethod
  def parse(clazz, s):
    if not isinstance(s, basestring):
      raise TypeError('mask to parse should be a string instead of: %s - %s' % (str(s), type(s)))
    names = s.split(clazz.DELIMITER)
    names = [ n.strip() for n in names if n.strip() ]
    result = 0
    for name in names:
      value = clazz._ENUM.parse_name(name)
      if value == None:
        raise ValueError('invalid value: %s' % (name))
      result |= value
    return result

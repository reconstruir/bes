#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .enum_loader import enum_loader, enum_loader_meta_class

class flag_enum(object):

  DELIMITER = '|'
  
  __metaclass__ = enum_loader_meta_class

  def __init__(self, value = 0):
    self.assign(value)

  def matches(self, mask):
    return (self.value & mask) != 0
    
  def __str__(self):
    v = []
    for n in self._ENUM.name_values:
      if self.matches(n.value):
        v.append(n.name)
    return self.DELIMITER.join(v)
    
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
      self.value = self._ENUM.parse_name(what)
    elif isinstance(what, int):
      self.value = what
    else:
      raise TypeError('invalid value: %s' % (str(what)))
  
  @property
  def value(self):
    return self._value

  @value.setter
  def value(self, value):
    self._ENUM.check_value(value)
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
    return clazz(clazz._ENUM.parse_name(s))
  
  @classmethod
  def parse_mask(clazz, s):
    if not isinstance(s, basestring):
      raise TypeError('mask to parse should be a string instead of: %s - %s' % (str(s), type(s)))
    names = s.split(clazz.DELIMITER)
    names = [ n.strip() for n in names if n.strip() ]
    result = 0
    for name in names:
      v = clazz.parse(name)
      if not v:
        return None
      result |= v.value
    return result

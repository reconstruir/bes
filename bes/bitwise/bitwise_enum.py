#!/usr/bin/env python
#-*- coding:utf-8 -*-

from bes.common import enum_loader

class _bitwise_enum_meta(type):
  'Cheesy enum.  Id rather use the one in python3 but i want to support python 2.7 with no exta deps.'
  
  def __new__(meta, name, bases, class_dict):
    clazz = type.__new__(meta, name, bases, class_dict)
    if clazz.__name__ != 'bitwise_enum':
      clazz._ENUM = enum_loader.load(clazz)
    return clazz

class bitwise_enum(object):

  __metaclass__ = _bitwise_enum_meta

  def __init__(self, value = None):
    value = value or self.DEFAULT
    self.assign(value)

  def __str__(self):
    return self._ENUM.value_to_name(self._value)
    
  def __eq__(self, other):
    if isinstance(other, self.__class__):
      return self.value == other.value
    elif isinstance(what, basestring):
      return self.value == self.parse(other)
    elif isinstance(what, int):
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
  
  def write_to_io(self, io):
    io.write(self._value, self.SIZE)
    
  def read_from_io(self, io):
    self.value = io.read(self.SIZE)

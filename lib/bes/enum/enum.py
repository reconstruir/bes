#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .enum_loader import enum_loader
from bes.common import string_util
from bes.system.compat import with_metaclass

class _enum_meta_class(type):
  'cheesy enum.  Id rather use the one in python3 but i want to support python 2.7 with no exta deps.'
  
  def __new__(meta, name, bases, class_dict):
    clazz = type.__new__(meta, name, bases, class_dict)
    if hasattr(clazz, '_ENUM'):
      raise RuntimeError('subclassing %s not allowed.' % (bases[-1]))
    e = enum_loader.load(clazz)
    if e:
      clazz._ENUM = e
    return clazz

class enum(with_metaclass(_enum_meta_class, object)):

  def __init__(self, value = None):
    value = value or self.DEFAULT
    self.assign(value)

  def __str__(self):
    return self._ENUM.value_to_name(self._value)
    
  def __eq__(self, other):
    if isinstance(other, self.__class__):
      return self.value == other.value
    elif string_util.is_string(other):
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
    elif string_util.is_string(what):
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

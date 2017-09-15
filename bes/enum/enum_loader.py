#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import inspect
from .enum_manager import enum_manager

class enum_loader_meta_class(type):
  'cheesy enum.  Id rather use the one in python3 but i want to support python 2.7 with no exta deps.'
  
  def __new__(meta, name, bases, class_dict):
    clazz = type.__new__(meta, name, bases, class_dict)
    if hasattr(clazz, '_ENUM'):
      raise RuntimeError('subclassing %s not allowed.' % (bases[-1]))
    e = enum_loader.load(clazz)
    if e:
      clazz._ENUM = e
    return clazz

class enum_loader(object):
  
  @classmethod
  def load(clazz, target):
    name_values = clazz.load_name_values(target)
    if not name_values:
      return None
    size = clazz.load_size(target)
    default_value = clazz.load_default_value(target)
    if not default_value:
      default_value = min([ x[1] for x in name_values])
      setattr(target, 'DEFAULT', default_value)
    e = enum_manager()
    for name, value in name_values:
      e.add_value(name, value)
    e.default_value = default_value
    return e
    
  @classmethod
  def load_size(clazz, target):
    size = getattr(target, 'SIZE', 1)
    if not size in [ 1, 2, 4, 8 ]:
      raise TypeError('Invalid SIZE.  Should be 1, 2, 4 or 8 instead of: %s' % (size))
    return size

  @classmethod
  def load_default_value(clazz, target):
    getattr(target, 'DEFAULT', None)

  @classmethod
  def load_name_values(clazz, target):

    members = inspect.getmembers(target)
    int_members = [ member for member in members if isinstance(member[1], int) ]
    if not int_members:
      return None

    names = [ f for f in target.__dict__ if not f.startswith('_') ]
    names = [ f for f in names if f not in [ 'SIZE', 'DEFAULT' ] ]
    values = [ getattr(target, name) for name in names ]
    for value in values:
      if not isinstance(value, int):
        raise TypeError('Value should be of type int instead of %s: %s' % (type(value), str(value)))
    assert len(names) == len(values)
    return zip(names, values)

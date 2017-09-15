#!/usr/bin/env python
#-*- coding:utf-8 -*-

from .enum import enum

class enum_loader(object):

  @classmethod
  def load(clazz, target):
    size = clazz.load_size(target)
    name_values = clazz.load_name_values(target)
    default_value = clazz.load_default_value(target)
    if not default_value:
      default_value = min([ x[1] for x in name_values])
      setattr(target, 'DEFAULT', default_value)
    e = enum()
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
    names = [ f for f in target.__dict__ if not f.startswith('_') ]
    names = [ f for f in names if f not in [ 'SIZE', 'DEFAULT' ] ]
    values = [ getattr(target, name) for name in names ]
    for value in values:
      if not isinstance(value, int):
        raise TypeError('Value should be of type int instead of %s: %s' % (type(value), str(value)))
    assert len(names) == len(values)
    return zip(names, values)

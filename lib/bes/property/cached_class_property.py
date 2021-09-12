#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class cached_class_property(object):
  'A decorator that works like cached_property, but at the class level'

  def __init__(self, factory):
    self._factory = factory
    
  def __get__(self, instance, owner):
    key = self._factory.__name__
    value = self._factory(owner)
    setattr(owner, key, value)
    return value
  

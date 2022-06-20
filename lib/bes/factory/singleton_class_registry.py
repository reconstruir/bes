#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.property.cached_class_property import cached_class_property

from .class_registry import class_registry

class singleton_class_registry(object):

  @cached_class_property
  def _registry(clazz):
    class_name_prefix = getattr(clazz, '__registry_class_name_prefix__', None)
    raise_on_existing = getattr(clazz, '__registry_raise_on_existing__', False)
    registry = class_registry(class_name_prefix = class_name_prefix,
                              raise_on_existing = raise_on_existing)
    return registry
  
  @classmethod
  def register(clazz, registree, name = None):
    return clazz._registry.register(registree, name = name)
    
  @classmethod
  def get(clazz, class_name):
    return clazz._registry.get(class_name)

  @classmethod
  def items(clazz):
    return clazz._registry.items()

  @classmethod
  def registry(clazz):
    return clazz._registry.registry()
  
  @classmethod
  def keys(clazz):
    return clazz._registry.keys()

  @classmethod
  def values(clazz):
    return clazz._registry.values()
  
  @classmethod
  def shortcut_keys(clazz):
    return clazz._registry.shortcut_keys()

  @classmethod
  def make(clazz, class_name):
    return clazz._registry.make(class_name)

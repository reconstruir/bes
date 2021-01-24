#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .class_registry import class_registry

class singleton_class_registry(object):

  _registry = class_registry(class_name_prefix = 'step_', raise_on_existing = False)

  @classmethod
  def _get_registry(clazz):
    registry = getattr(clazz, '__registry', None)
    if not registry:
      class_name_prefix = getattr(clazz, '__registry_class_name_prefix__', None)
      raise_on_existing = getattr(clazz, '__registry_raise_on_existing__', False)
      registry = class_registry(class_name_prefix = class_name_prefix,
                                raise_on_existing = raise_on_existing)
      setattr(clazz, '__registry', registry)
    return registry
  
  @classmethod
  def register(clazz, registree, name = None):
    return clazz._get_registry().register(registree, name = name)
    
  @classmethod
  def get(clazz, class_name):
    return clazz._get_registry().get(class_name)

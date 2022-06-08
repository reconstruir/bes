#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import sys
from bes.common.string_util import string_util

class class_registry(object):

  def __init__(self, class_name_prefix = None, raise_on_existing = True):
    self._class_name_prefix = class_name_prefix
    self._raise_on_existing = raise_on_existing
    self._registry = {}
  
  def register(self, registree, name = None):
    name = name or registree.__name__
    existing = self._registry.get(name, None)
    if existing:
      if self._raise_on_existing:
        raise ValueError('class with name \"%s\" already registered: %s' % (name, str(registree)))
      return
    self._registry[name] = registree
    if self._class_name_prefix and self._class_name_prefix in name:
      name_no_prefix = name.replace(self._class_name_prefix, '')
      self._registry[name_no_prefix] = registree
    self._add_to_global_sys_modules(registree)
      
  def get(self, class_name):
    return self._registry.get(class_name, None)

  def make(self, class_name):
    object_class = self.get(class_name)
    return object_class()

  def items(self):
    return self._registry.items()
  
  @classmethod
  def _add_to_global_sys_modules(clazz, registree):
    '''
    if registree has a __bes_add_to_sys_modules__ attribute, use it
    to make it available at the global module level so that pickling works.
    '''
    module_name = getattr(registree, '__bes_add_to_sys_modules__', None)
    if module_name:
      setattr(sys.modules[module_name], registree.__name__, registree)

#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import string_util
from collections import namedtuple

class class_registry(object):

  def __init__(self, class_name_prefix = None, raise_on_existing = True):
    self._class_name_prefix = class_name_prefix
    self._raise_on_existing = raise_on_existing
    self._registry = {}
  
  def register_class(self, registree):
    name = registree.__name__
    existing = self._registry.get(name, None)
    if existing:
      if self._raise_on_existing:
        raise ValueError('class with name \"%s\" already registered: %s' % (name, str(registree)))
      return
    self._registry[name] = registree
    if self._class_name_prefix and name.startswith(self._class_name_prefix):
      name_no_prefix = string_util.remove_head(name, self._class_name_prefix)
      self._registry[name_no_prefix] = registree
    
  @classmethod
  def get(self, class_name):
    return self._registry.get(class_name, None)

  def make(self, class_name):
    object_class = self.get(class_name)
    return object_class()

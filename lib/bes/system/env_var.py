#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os

class env_var(object):

  def __init__(self, target, name):
    self._target = target
    self._name = name

  @property
  def name(self):
    return self._name

  @property
  def value(self):
    return self._target.get(self._name, None)

  @value.setter
  def value(self, value):
    self._target[self._name] = value

  @property
  def path(self):
    value = self.value
    if not value:
      return []
    return self.path_cleanup(self.path_split(value))

  @path.setter
  def path(self, value):
    assert isinstance(value, list)
    clean_value = self.path_cleanup(value)
    self.value = self.path_join(clean_value)

  def cleanup(self):
    self.path = self.path # the setter for path does the cleanup

  def append(self, p):
    self.remove(p)
    if not isinstance(p, list):
      p = [ p ]
    self.path = self.path + p

  def remove(self, p):
    path = [ item for item in self.path if item != p ]
    self.path = path

  def prepend(self, p):
    if not isinstance(p, list):
      p = [ p ]
    self.path = p + self.path

  @classmethod
  def path_cleanup(clazz, value):
    assert isinstance(value, list)
    seen = {}
    unique_value = [ seen.setdefault(x, x) for x in value if x not in seen ]
    return [ x for x in unique_value if x ]

  @classmethod
  def path_split(clazz, p):
    return p.split(os.pathsep)

  @classmethod
  def path_join(clazz, l):
    assert isinstance(l, list)
    return os.pathsep.join(l)

  def get(self, name, default_value = None):
    return self._target.get(name, default_value)
  
  @property
  def is_set(self):
    return self._name in self._target
  
class os_env_var(env_var):
  def __init__(self, name):
    super(os_env_var, self).__init__(os.environ, name)

#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from collections import namedtuple
from bes.common import check, variable
from bes.system import os_env_var

# From https://stackoverflow.com/questions/4037481/caching-attributes-of-classes-in-python
class env_var_property(object):
  """/home/ramiro/proj/rebuild/lib/rebuild/credentials/credential.py
  Descriptor (non-data) for building an attribute on-demand on first use.
  Based on From https://stackoverflow.com/questions/4037481/caching-attributes-of-classes-in-python
  """
  def __init__(self, factory):
    """
    <factory> is called such: factory(instance) to build the attribute.
    """
    self._attr_name = factory.__name__
    self._factory = factory

  def __get__(self, instance, owner):
    # Build the attribute.
    attr = self._factory(instance)
    attr = self.resolve_value(attr)
    
    # Cache the value; hide ourselves.
    setattr(instance, self._attr_name, attr)

    return attr

  @classmethod
  def resolve_value(clazz, value):
    value = clazz.resolve_home_tilde(value)
    value = clazz.resolve_env_vars(value)
    return value
  
  @classmethod
  def resolve_home_tilde(clazz, value):
    if not check.is_string(value):
      return value
    if value.startswith('~/'):
      return path.expanduser(value)
    return value
  
  @classmethod
  def resolve_env_vars(clazz, value):
    if not check.is_string(value):
      return value
    variables = variable.find_variables(value)
    substitutions = {}
    for var in variables:
      os_var = os_env_var(var)
      if not os_var.is_set:
        raise ValueError('%s not set in the current environment: \"%s\"' % (var, value))
      substitutions[var] = os_var.value
    return variable.substitute(value, substitutions, word_boundary = False)

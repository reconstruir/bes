#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.property.cached_property import cached_property
from bes.system.check import check
from bes.system.log import logger

from .bfile_attr_value_factory_base import bfile_attr_value_factory_base
from .bfile_attr_value import bfile_attr_value
from .bfile_attr_value_list import bfile_attr_value_list
from .bfile_attr_error import bfile_attr_error

class bfile_attr_value_registry(object):

  _log = logger('attr')
  
  class _factory_item(object):
 
    def __init__(self, factory_class):
      self._factory_class = factory_class

    @cached_property
    def factory(self):
      return self._factory_class()

  _factories = {}
  @classmethod
  def register_factory(clazz, factory_class):
    check.check_class(factory_class, bfile_attr_value_factory_base)

    clazz._log.log_method_d()
    raw_values_list = factory_class.cached_descriptions
    try:
      values = check.check_bfile_attr_value_list(raw_values_list)
    except TypeError as ex:
      raise bfile_attr_error(f'values should be a sequence of "bfile_attr_value" or tuples: "{raw_values_list}" - {type(raw_values_list)}')
    for next_value in values:
      if next_value.key in clazz._factories:
        raise bfile_attr_error(f'value already registered: "{next_value.key}"')
      clazz._factories[next_value.key] = next_value
      clazz._log.log_d(f'registered next_value {next_value.key}')

  @classmethod
  def unregister_factory(clazz, factory_class):
    check.check_class(factory_class, bfile_attr_value_factory_base)

    clazz._log.log_method_d()
    raw_values_list = factory_class.cached_descriptions
    try:
      values = check.check_bfile_attr_value_list(raw_values_list)
    except TypeError as ex:
      raise bfile_attr_error(f'values should be a sequence of "bfile_attr_value" or tuples: "{raw_values_list}" - {type(raw_values_list)}')
    for next_value in values:
      if next_value.key in clazz._factories:
        del clazz._factories[next_value.key]
        clazz._log.log_d(f'unregistered next_value {next_value.key}')
      
  @classmethod
  def unregister_all(clazz):
    clazz._factories = {}
      
  @classmethod
  def get_value(clazz, key, raise_error = True):
    check.check_string(key)

    value = clazz._factories.get(key, None)
    clazz._log.log_d(f'key={key} value={value}')
    if raise_error and not value:
      raise bfile_attr_error(f'no value registered for: "{key}"')
    return value

  @classmethod
  def has_value(clazz, key):
    check.check_string(key)

    return clazz.get_value(key, raise_error = False) != None

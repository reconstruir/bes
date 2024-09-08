#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.property.cached_property import cached_property
from bes.system.check import check
from bes.system.log import logger

from .bf_attr2_desc_factory_base import bf_attr2_desc_factory_base
from .bf_attr2_desc import bf_attr2_desc
from .bf_attr2_desc_list import bf_attr2_desc_list
from .bf_attr2_error import bf_attr2_error

class bf_attr2_desc_registry(object):

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
    check.check_class(factory_class, bf_attr2_desc_factory_base)

    clazz._log.log_method_d()
    raw_values_list = factory_class.cached_descriptions
    try:
      values = check.check_bf_attr2_desc_list(raw_values_list)
    except TypeError as ex:
      raise bf_attr2_error(f'values should be a sequence of "bf_attr2_desc" or tuples: "{raw_values_list}" - {type(raw_values_list)}')
    for next_value in values:
      if next_value.key in clazz._factories:
        old_value = clazz._factories[next_value.key]
        if next_value != old_value:
          raise bf_attr2_error(f'value already registered: "{next_value.key}"')
      clazz._factories[next_value.key] = next_value
      clazz._log.log_d(f'registered next_value {next_value.key}')

  @classmethod
  def unregister_factory(clazz, factory_class):
    check.check_class(factory_class, bf_attr2_desc_factory_base)

    clazz._log.log_method_d()
    raw_values_list = factory_class.cached_descriptions
    try:
      values = check.check_bf_attr2_desc_list(raw_values_list)
    except TypeError as ex:
      raise bf_attr2_error(f'values should be a sequence of "bf_attr2_desc" or tuples: "{raw_values_list}" - {type(raw_values_list)}')
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
      raise bf_attr2_error(f'no value registered for: "{key}"')
    return value

  @classmethod
  def has_value(clazz, key):
    check.check_string(key)

    return clazz.get_value(key, raise_error = False) != None

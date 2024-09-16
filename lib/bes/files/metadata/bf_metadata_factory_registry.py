#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.property.cached_property import cached_property
from bes.system.check import check
from bes.system.log import logger

from .bf_metadata_factory_base import bf_metadata_factory_base
from .bf_metadata_desc import bf_metadata_desc
from .bf_metadata_desc_list import bf_metadata_desc_list
from .bf_metadata_key import bf_metadata_key
from .bf_metadata_error import bf_metadata_error

class bf_metadata_factory_registry(object):

  _log = logger('metadata')
  
  class _factory_item(object):
 
    def __init__(self, factory_class):
      self._factory_class = factory_class

    @cached_property
    def factory(self):
      return self._factory_class()

  _factories = {}
  @classmethod
  def register_factory(clazz, factory_class):
    check.check_class(factory_class, bf_metadata_factory_base)

    clazz._log.log_method_d()

    descriptions = clazz.check_descriptions(factory_class.cached_descriptions)
    for description in descriptions:
      if description.key in clazz._factories:
        clazz._log.log_w(f'overriding existing description {description.key} {description.getter}')
      clazz._factories[description.key] = description
      clazz._log.log_d(f'registered description {description.key} {description.getter}')

  @classmethod
  def check_descriptions(clazz, raw_descriptions):
    descriptions = []
    try:
      for raw_description in raw_descriptions:
        description = check.check_bf_metadata_desc(raw_description)
        descriptions.append(description)
    except TypeError as ex:
      raise bf_metadata_error(f'description should be a sequence of "bf_metadata_desc" or tuples: "{raw_description}" - {type(raw_description)}\n{str(ex)}')
    return descriptions
      
  @classmethod
  def unregister_factory(clazz, factory_class):
    check.check_class(factory_class, bf_metadata_factory_base)

    clazz._log.log_method_d()
    descriptions = clazz.check_descriptions(factory_class.cached_descriptions)
    for description in descriptions:
      if description.key in clazz._factories:
        del clazz._factories[description.key]
        clazz._log.log_d(f'unregistered description {description.key}')
      
  @classmethod
  def unregister_all(clazz):
    clazz._factories = {}
      
  @classmethod
  def get_description(clazz, key, raise_error = True):
    key = check.check_bf_metadata_key(key)

    description = clazz._factories.get(key, None)
    clazz._log.log_d(f'key={key} description={description}')
    if raise_error and not description:
      raise bf_metadata_error(f'no description registered for: "{key}"')
    return description

  @classmethod
  def has_description(clazz, key):
    key = check.check_bf_metadata_key(key)

    return clazz.get_description(key, raise_error = False) != None

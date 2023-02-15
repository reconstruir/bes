#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.property.cached_property import cached_property
from bes.system.check import check
from bes.system.log import logger

from ..attributes.bfile_attr_error import bfile_attr_error

from .bfile_metadata_factory_base import bfile_metadata_factory_base
from .bfile_metadata_handler import bfile_metadata_handler
from .bfile_metadata_handler_list import bfile_metadata_handler_list

class bfile_metadata_factory_registry(object):

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
    check.check_class(factory_class, bfile_metadata_factory_base)

    clazz._log.log_method_d()
    raw_handlers_list = factory_class.handlers()
    try:
      handlers = check.check_bfile_metadata_handler_list(raw_handlers_list)
    except TypeError as ex:
      raise bfile_attr_error(f'handlers should be a sequence of "bfile_metadata_handler" or tuples: "{raw_handlers_list}" - {type(raw_handlers_list)}')
    for handler in handlers:
      if handler.factory_key in clazz._factories:
        raise bfile_attr_error(f'getter already registered: "{handler.factory_key}"')
      clazz._factories[handler.factory_key] = handler
      clazz._log.log_d(f'registered handler {handler.factory_key} {handler.getter}')

  @classmethod
  def clear_all(clazz):
    clazz._factories = {}
      
  @classmethod
  def get_handler(clazz, domain, group, name, version, raise_error = True):
    check.check_string(domain)
    check.check_string(group)
    check.check_string(name)
    version = check.check_semantic_version(version)
    
    handler_key = bfile_metadata_handler.make_factory_key(domain, group, name, version)
    handler = clazz._factories.get(handler_key, None)
    clazz._log.log_d(f'handler_key={handler_key} handler={handler}')
    if raise_error and not handler:
      raise bfile_attr_error(f'no handler registered for: "{handler_key}"')
    return handler

  @classmethod
  def has_handler(clazz, domain, group, name, version):
    check.check_string(domain)
    check.check_string(group)
    check.check_string(name)
    version = check.check_semantic_version(version)

    return clazz.get_handler(domain, group, name, version, raise_error = False) != None

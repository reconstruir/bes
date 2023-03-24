#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.property.cached_property import cached_property
from bes.system.check import check
from bes.system.log import logger

from .bf_metadata_factory_base import bf_metadata_factory_base
from .bf_metadata_handler import bf_metadata_handler
from .bf_metadata_handler_list import bf_metadata_handler_list
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

    handlers = clazz.check_handlers(factory_class.cached_handlers)
    for handler in handlers:
      if handler.key in clazz._factories:
        raise bf_metadata_error(f'getter already registered: "{handler.key}"')
      clazz._factories[handler.key] = handler
      clazz._log.log_d(f'registered handler {handler.key} {handler.getter}')

  @classmethod
  def check_handlers(clazz, raw_handlers):
    handlers = []
    try:
      for raw_handler in raw_handlers:
        handler = check.check_bf_metadata_handler(raw_handler)
        handlers.append(handler)
    except TypeError as ex:
      raise bf_metadata_error(f'handler should be a sequence of "bf_metadata_handler" or tuples: "{raw_handler}" - {type(raw_handler)}\n{str(ex)}')
    return handlers
      
  @classmethod
  def unregister_factory(clazz, factory_class):
    check.check_class(factory_class, bf_metadata_factory_base)

    clazz._log.log_method_d()
    handlers = clazz.check_handlers(factory_class.cached_handlers)
    for handler in handlers:
      if handler.key in clazz._factories:
        del clazz._factories[handler.key]
        clazz._log.log_d(f'unregistered handler {handler.key}')
      
  @classmethod
  def unregister_all(clazz):
    clazz._factories = {}
      
  @classmethod
  def get_handler(clazz, key, raise_error = True):
    key = check.check_bf_metadata_key(key)

    handler = clazz._factories.get(key, None)
    clazz._log.log_d(f'key={key} handler={handler}')
    if raise_error and not handler:
      raise bf_metadata_error(f'no handler registered for: "{key}"')
    return handler

  @classmethod
  def has_handler(clazz, key):
    key = check.check_bf_metadata_key(key)

    return clazz.get_handler(key, raise_error = False) != None

#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta

from bes.system.compat import with_metaclass
from bes.system.check import check
from bes.property.cached_class_property import cached_class_property

class _bf_attr_handler_factory_meta(ABCMeta):
  
  def __new__(meta, name, bases, class_dict):
    clazz = ABCMeta.__new__(meta, name, bases, class_dict)
    if name != 'bf_attr_handler_factory_base':
      from .bf_attr_description_registry import bf_attr_description_registry
      bf_attr_description_registry.register_factory(clazz)
    return clazz

class bf_attr_handler_factory_base(with_metaclass(_bf_attr_handler_factory_meta)):

  @cached_class_property
  def attr(clazz):
    'Provide a property that returns the main attr class so handler can use it.'
    from .bf_attr import bf_attr
    return bf_attr

  @cached_class_property
  def encoding(clazz):
    'Provide a property that returns the encoding class so handler can use it.'
    from .bf_attr_encoding import bf_attr_encoding
    return bf_attr_encoding
  
  @cached_class_property
  def cached_descriptions(clazz):
    return clazz.descriptions()
  
  @classmethod
  @abstractmethod
  def descriptions(clazz):
    'Return a list of value descriptions this factory supports.'
    raise NotImplemented('descriptions')
  
check.register_class(bf_attr_handler_factory_base, name = 'bf_attr_handler_factory', include_seq = False)

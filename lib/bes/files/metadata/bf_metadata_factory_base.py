#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta

from bes.system.compat import with_metaclass
from bes.system.check import check
from bes.property.cached_class_property import cached_class_property

from bes.system.compat import with_metaclass

class _bf_metadata_factory_meta(ABCMeta):
  
  def __new__(meta, name, bases, class_dict):
    clazz = ABCMeta.__new__(meta, name, bases, class_dict)
    if name != 'bf_metadata_factory_base':
      from .bf_metadata_factory_registry import bf_metadata_factory_registry
      #print(f'CACA: register: name={name} __name__={clazz.__name__}')
      bf_metadata_factory_registry.register_factory(clazz)
    return clazz

class bf_metadata_factory_base(with_metaclass(_bf_metadata_factory_meta)):

  @cached_class_property
  def metadata(clazz):
    'Provide a property that returns the main metadata class so handler can use it.'
    from .bf_metadata import bf_metadata
    return bf_metadata

  @cached_class_property
  def encoding(clazz):
    'Provide a property that returns the encoding class so handler can use it.'
    from ..attr.bf_attr_encoding import bf_attr_encoding
    return bf_attr_encoding
  
  @cached_class_property
  def cached_handlers(clazz):
    return clazz.handlers()
  
  @classmethod
  @abstractmethod
  def handlers(clazz):
    'Return a list of handlers this factory supports.'
    raise NotImplemented('handlers')
  
check.register_class(bf_metadata_factory_base, name = 'bf_metadata_factory', include_seq = False)
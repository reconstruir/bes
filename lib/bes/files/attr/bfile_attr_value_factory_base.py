#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta

from bes.system.compat import with_metaclass
from bes.system.check import check
from bes.property.cached_class_property import cached_class_property

class _bfile_attr_value_factory_meta(ABCMeta):
  
  def __new__(meta, name, bases, class_dict):
    clazz = ABCMeta.__new__(meta, name, bases, class_dict)
    if name != 'bfile_attr_value_factory_base':
      from .bfile_attr_value_registry import bfile_attr_value_registry
      bfile_attr_value_registry.register_factory(clazz)
    return clazz

class bfile_attr_value_factory_base(with_metaclass(_bfile_attr_value_factory_meta)):

  @cached_class_property
  def attr(clazz):
    'Provide a property that returns the main attr class so handler can use it.'
    from .bfile_attr import bfile_attr
    return bfile_attr

  @cached_class_property
  def encoding(clazz):
    'Provide a property that returns the encoding class so handler can use it.'
    from .bfile_attr_encoding import bfile_attr_encoding
    return bfile_attr_encoding
  
  @cached_class_property
  def cached_descriptions(clazz):
    return clazz.descriptions()
  
  @classmethod
  @abstractmethod
  def descriptions(clazz):
    'Return a list of value descriptions this factory supports.'
    raise NotImplemented('descriptions')
  
check.register_class(bfile_attr_value_factory_base, name = 'bfile_attr_handler_factory', include_seq = False)

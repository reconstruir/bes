#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta

from bes.system.compat import with_metaclass
from bes.system.check import check
from bes.property.cached_class_property import cached_class_property

from .bfile_attr_encoding import bfile_attr_encoding

class _bfile_attr_value_factory_meta(ABCMeta):
  
  def __new__(meta, name, bases, class_dict):
    clazz = ABCMeta.__new__(meta, name, bases, class_dict)
    if name != 'bfile_attr_value_factory_base':
      from .bfile_attr_value_registry import bfile_attr_value_registry
      #print(f'CACA: register: name={name} __name__={clazz.__name__}')
      bfile_attr_value_registry.register_factory(clazz)
    return clazz

class bfile_attr_value_factory_base(with_metaclass(_bfile_attr_value_factory_meta, bfile_attr_encoding)):

  @cached_class_property
  def attr_class(clazz):
    'Provide a property that returns the main attr class so handler can use it.'
    from .bfile_attr import bfile_attr
    return bfile_attr
  
  @classmethod
  @abstractmethod
  def values(clazz):
    'Return a list of values this factory supports.'
    raise NotImplemented('values')
  
check.register_class(bfile_attr_value_factory_base, name = 'bfile_attr_handler_factory', include_seq = False)

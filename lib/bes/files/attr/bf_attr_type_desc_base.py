#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta

from bes.system.check import check
from bes.property.cached_class_property import cached_class_property

class _bf_attr_type_desc_meta(ABCMeta):
  
  def __new__(meta, name, bases, class_dict):
    clazz = ABCMeta.__new__(meta, name, bases, class_dict)
    if name != 'bf_attr_type_desc_base':
      pass
      #from .bf_attr_desc_registry import bf_attr_desc_registry
      #bf_attr_desc_registry.register_factory(clazz)
    return clazz

class bf_attr_type_desc_base(metaclass = _bf_attr_type_desc_meta):

  @classmethod
  @abstractmethod
  def name(clazz):
    'Return the name for this type'
    raise NotImplemented('name')

  @classmethod
  @abstractmethod
  def encode(clazz, value):
    'Encode value into bytes'
    raise NotImplemented('encode')

  @classmethod
  @abstractmethod
  def decode(clazz, value_bytes):
    'Decode value_bytes into a value'
    raise NotImplemented('decode')

  @classmethod
  @abstractmethod
  def check(clazz, value):
    'Check type of value'
    raise NotImplemented('check')
  
check.register_class(bf_attr_type_desc_base, name = 'bf_attr_type_desc', include_seq = False)

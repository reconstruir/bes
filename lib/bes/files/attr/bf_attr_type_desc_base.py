#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta

from bes.system.compat import with_metaclass
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

class bf_attr_type_desc_base(with_metaclass(_bf_attr_type_desc_meta)):

  @classmethod
  @abstractmethod
  def name(clazz):
    'Return the name for this type'
    raise NotImplemented('name')

  @classmethod
  @abstractmethod
  def encoder(clazz):
    'Return encoder function for this type'
    raise NotImplemented('encoder')

  @classmethod
  @abstractmethod
  def decoder(clazz):
    'Return decoder function for this type'
    raise NotImplemented('decoder')

  @classmethod
  @abstractmethod
  def checker(clazz):
    'Return checker function for this type'
    raise NotImplemented('checker')
  
  @classmethod
  @abstractmethod
  def description(clazz):
    'Return a description for this type.'
    raise NotImplemented('description')

  @classmethod
  def decode(clazz, value):
    return clazz.decoder()(value)

  @classmethod
  def encode(clazz, value):
    return clazz.encoder()(value)

  @classmethod
  def check(clazz, value):
    return clazz.checker()(value)
  
check.register_class(bf_attr_type_desc_base, name = 'bf_attr_type_desc', include_seq = False)

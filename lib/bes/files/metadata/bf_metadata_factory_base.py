#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta

from bes.system.check import check
from bes.property.cached_class_property import cached_class_property

from bes.system.log import logger

class _bf_metadata_factory_meta(ABCMeta):

  _log = logger('metadata')
  
  def __new__(meta, name, bases, class_dict):
    clazz = ABCMeta.__new__(meta, name, bases, class_dict)
    if name != 'bf_metadata_factory_base':
      from .bf_metadata_factory_registry import bf_metadata_factory_registry
      _bf_metadata_factory_meta._log.log_d(f'_bf_metadata_factory_meta: register: name={name} __name__={clazz.__name__}')
      bf_metadata_factory_registry.register_factory(clazz)
    return clazz

class bf_metadata_factory_base(metaclass = _bf_metadata_factory_meta):

  @cached_class_property
  def metadata(clazz):
    'Provide a property that returns the main metadata class so subclasses can use it.'
    from .bf_metadata import bf_metadata
    return bf_metadata

  @cached_class_property
  def cached_descriptions(clazz):
    return clazz.descriptions()
  
  @classmethod
  @abstractmethod
  def descriptions(clazz):
    'Return a list of descriptions this factory supports.'
    raise NotImplemented('descriptions')
  
check.register_class(bf_metadata_factory_base, name = 'bf_metadata_factory', include_seq = False)

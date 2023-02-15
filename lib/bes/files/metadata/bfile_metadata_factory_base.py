#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta

from bes.system.compat import with_metaclass
from bes.system.check import check
from bes.property.cached_class_property import cached_class_property

from .bfile_metadata_encoding import bfile_metadata_encoding

class bfile_metadata_factory_base(with_metaclass(ABCMeta, bfile_metadata_encoding)):

  @cached_class_property
  def metadata_class(clazz):
    'Provide a property that returns the main metadata class so handler can use it.'
    from .bfile_metadata import bfile_metadata
    return bfile_metadata
  
  @classmethod
  @abstractmethod
  def handlers(clazz):
    'Return a list of handlers this factory supports.'
    raise NotImplemented('handlers')
  
check.register_class(bfile_metadata_factory_base, name = 'bfile_attr_factory', include_seq = False)

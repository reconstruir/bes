#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta

from bes.system.compat import with_metaclass
from bes.system.check import check

from .bfile_attr_decode import bfile_attr_decode

class bfile_attr_factory_base(with_metaclass(ABCMeta, bfile_attr_decode)):

  @classmethod
  @abstractmethod
  def handlers(clazz):
    'Return a list of handlers this factory supports.'
    raise NotImplemented('handlers')
  
check.register_class(bfile_attr_factory_base, name = 'bfile_attr_factory', include_seq = False)

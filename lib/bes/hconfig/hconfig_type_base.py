#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta

from ..system.compat import with_metaclass
from ..system.check import check

class hconfig_type_base(with_metaclass(ABCMeta, object)):

  @classmethod
  @abstractmethod
  def cast_value(clazz, value):
    'Cast a value.'
    raise NotImplemented('cast_value')

check.register_class(hconfig_type_base, name = 'hconfig_type', include_seq = False)

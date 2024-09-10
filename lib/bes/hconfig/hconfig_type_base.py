#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta

from ..system.check import check

class hconfig_type_base(object, metaclass = ABCMeta):

  @classmethod
  @abstractmethod
  def cast(clazz, value, root):
    'Cast a value.'
    raise NotImplementedError('cast')

check.register_class(hconfig_type_base, name = 'hconfig_type', include_seq = False)

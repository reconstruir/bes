#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod
from abc import ABCMeta

from ..system.check import check
from ..system.log import logger
from ..property.cached_class_property import cached_class_property

class bcli_type_i(metaclass = ABCMeta):

  _log = logger('bcli')
  
  @classmethod
  @abstractmethod
  def name_str(clazz):
    raise NotImplementedError(f'name_str')

  @cached_class_property
  def name(clazz):
    return clazz.name_str()
  
  @classmethod
  @abstractmethod
  def type_function(clazz):
    raise NotImplementedError(f'type_function')

  @cached_class_property
  def type(clazz):
    return clazz.type_function()
  
  @classmethod
  @abstractmethod
  def parse(clazz, text):
    raise NotImplementedError(f'parse')

  @classmethod
  @abstractmethod
  def check(clazz, value, allow_none = False):
    raise NotImplementedError(f'check')

check.register_class(bcli_type_i, name = 'bcli_type', include_seq = False)

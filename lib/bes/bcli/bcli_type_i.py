#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod
from abc import ABCMeta

from ..system.check import check
from ..system.log import logger
from ..property.cached_property import cached_property

class bcli_type_i(metaclass = ABCMeta):

  _log = logger('bcli')
  
  @abstractmethod
  def name(self):
    raise NotImplementedError(f'name')

  @abstractmethod
  def type_function(self):
    raise NotImplementedError(f'type_function')

  @cached_property
  def type(self):
    return self.type_function()()
  
  @abstractmethod
  def parse(self, text):
    raise NotImplementedError(f'parse')

  @abstractmethod
  def check(self, value, allow_none = False):
    raise NotImplementedError(f'check')
  
check.register_class(bcli_type_i, name = 'bcli_type', include_seq = False)

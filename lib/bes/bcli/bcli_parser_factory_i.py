#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod
from abc import ABC

from ..system.check import check
from ..system.log import logger

class bcli_parser_factory_i(ABC):

  _log = logger('bcli')

  @classmethod
  @abstractmethod
  def path(clazz):
    raise NotImplementedError(f'path')
  
  @abstractmethod
  def has_sub_parsers(self):
    raise NotImplementedError(f'has_sub_parsers')
  
  @abstractmethod
  def add_sub_parsers(self, subparsers):
    raise NotImplementedError(f'add_sub_parsers')

  @abstractmethod
  def add_arguments(self, parser):
    raise NotImplementedError(f'add_arguments')
  
check.register_class(bcli_parser_factory_i, name = 'bcli_parser_maker', include_seq = False)

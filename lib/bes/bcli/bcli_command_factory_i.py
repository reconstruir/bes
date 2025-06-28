#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod
from abc import ABC

from ..system.check import check
from ..system.log import logger

class bcli_command_factory_i(ABC):

  _log = logger('bcli')

  @classmethod
  @abstractmethod
  def path(clazz):
    raise NotImplementedError(f'path')

  @classmethod
  @abstractmethod
  def description(clazz):
    raise NotImplementedError(f'description')
  
  @abstractmethod
  def error_class(self):
    raise NotImplementedError(f'error_class')

  @abstractmethod
  def options_class(self):
    raise NotImplementedError(f'options_class')
  
  @abstractmethod
  def has_commands(self):
    raise NotImplementedError(f'has_commands')
  
  @abstractmethod
  def add_commands(self, subparsers):
    raise NotImplementedError(f'add_commands')

  @abstractmethod
  def add_arguments(self, parser):
    raise NotImplementedError(f'add_arguments')

  @abstractmethod
  def handler_class(self):
    raise NotImplementedError(f'handler_class')

check.register_class(bcli_command_factory_i, name = 'bcli_parser_factory', include_seq = False)

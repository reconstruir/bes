#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import abc

class bcli_command_factory_i(abc.ABC):

  @classmethod
  @abc.abstractmethod
  def path(clazz):
    raise NotImplementedError(f'path')

  @classmethod
  @abc.abstractmethod
  def description(clazz):
    raise NotImplementedError(f'description')
  
  @abc.abstractmethod
  def error_class(self):
    raise NotImplementedError(f'error_class')

  @abc.abstractmethod
  def options_class(self):
    raise NotImplementedError(f'options_class')
  
  @abc.abstractmethod
  def has_commands(self):
    raise NotImplementedError(f'has_commands')
  
  @abc.abstractmethod
  def add_commands(self, subparsers):
    raise NotImplementedError(f'add_commands')

  @abc.abstractmethod
  def add_arguments(self, parser):
    raise NotImplementedError(f'add_arguments')

  @abc.abstractmethod
  def handler_class(self):
    raise NotImplementedError(f'handler_class')

  @abc.abstractmethod
  def supported_platforms(self):
    raise NotImplementedError(f'supported_platforms')

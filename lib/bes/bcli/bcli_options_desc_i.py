 #-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta

class bcli_options_desc_i(metaclass = ABCMeta):

  @abstractmethod
  def name(self):
    raise NotImplementedError('name')
  
  @abstractmethod
  def types(self):
    raise NotImplementedError('types')

  @abstractmethod
  def options_desc(self):
    raise NotImplementedError('options_desc')

  @abstractmethod
  def variables(self):
    raise NotImplementedError('variables')

  @abstractmethod
  def defaults(self):
    raise NotImplementedError('defaults')
  

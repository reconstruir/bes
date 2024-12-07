 #-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta

class bcli_options_desc_i(metaclass = ABCMeta):

  @abstractmethod
  def _types(self):
    raise NotImplementedError('_types')

  @abstractmethod
  def _variables(self):
    raise NotImplementedError('_variables')

  @abstractmethod
  def _error_class(self):
    raise NotImplementedError('_error_class')
  
  @abstractmethod
  def _options_desc(self):
    raise NotImplementedError('_options_desc')


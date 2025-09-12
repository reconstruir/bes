#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta

from ..system.check import check

class properties_file_formatter_base(object, metaclass = ABCMeta):

  @abstractmethod
  def delimiter(self):
    raise NotImplementedError('delimiter')
  
  @abstractmethod
  def parse_value(self, key, value):
    raise NotImplementedError('parse_value')

  @abstractmethod
  def value_to_text(self, key, value):
    raise NotImplementedError('value_to_text')

  @abstractmethod
  def key_value_to_text(self, key, value):
    raise NotImplementedError('key_value_to_text')

check.register_class(properties_file_formatter_base, include_seq = False, name = 'properties_file_formatter')

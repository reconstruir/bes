#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta

from bes.system.compat import with_metaclass
from bes.common.check import check

class properties_file_formatter_base(with_metaclass(ABCMeta, object)):

  @abstractmethod
  def delimiter(self):
    raise NotImplemented('delimiter')
  
  @abstractmethod
  def format_get(self, value):
    raise NotImplemented('format_get')

  @abstractmethod
  def format_set(self, value):
    raise NotImplemented('format_set')

  @abstractmethod
  def format_key_value(self, key, value):
    raise NotImplemented('format_key_value')

check.register_class(properties_file_formatter_base, include_seq = False, name = 'properties_file_formatter')

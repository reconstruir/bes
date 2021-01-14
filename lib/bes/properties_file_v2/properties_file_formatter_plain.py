#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .properties_file_formatter_base import properties_file_formatter_base

class properties_file_formatter_plain(properties_file_formatter_base):

  #@abstractmethod
  def delimiter(self):
    return '='
  
  #@abstractmethod
  def format_get(self, value):
    return value

  #@abstractmethod
  def format_set(self, value):
    return value

  #@abstractmethod
  def format_key_value(self, key, value):
    return '{}{}{}'.format(key, self.delimiter(), value)

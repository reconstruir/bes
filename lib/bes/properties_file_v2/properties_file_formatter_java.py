#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.string_util import string_util

from .properties_file_formatter_base import properties_file_formatter_base

class properties_file_formatter_java(properties_file_formatter_base):

  #@abstractmethod
  def delimiter(self):
    return '='
  
  #@abstractmethod
  def parse_value(self, key, value):
    return value

  #@abstractmethod
  def value_to_text(self, key, value):
    return value

  #@abstractmethod
  def key_value_to_text(self, key, value):
    return '{}{}{}'.format(key, self.delimiter(), value)

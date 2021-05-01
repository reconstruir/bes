#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.string_util import string_util

from .properties_file_formatter_base import properties_file_formatter_base

class properties_file_formatter_yaml(properties_file_formatter_base):

  _QUOTE_CHAR = "'"
  
  #@abstractmethod
  def delimiter(self):
    return ':'
  
  #@abstractmethod
  def parse_value(self, key, value):
    return string_util.unquote(value)

  #@abstractmethod
  def value_to_text(self, key, value):
    if self._value_is_number(value):
      return string_util.quote(value, quote_char = self._QUOTE_CHAR)
    return value

  #@abstractmethod
  def key_value_to_text(self, key, value):
    return '{}{} {}'.format(key, self.delimiter(), value)

  @classmethod 
  def _value_is_number(clazz, value):
    try:
      float(value)
      return True
    except:
      return False

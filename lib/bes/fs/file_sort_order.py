#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_type_i import bcli_type_i
from bes.enum_util.checked_enum import checked_enum

class file_sort_order(checked_enum):
  DATE = 'date'
  DEPTH = 'depth'
  FILENAME = 'filename'
  SIZE = 'size'

file_sort_order.register_check_class()

class cli_file_sort_order_type(bcli_type_i):

  @classmethod
  #@abstractmethod
  def name_str(clazz):
    return 'cli_file_sort_order_type'

  @classmethod
  #@abstractmethod
  def type_function(clazz):
    return file_sort_order

  @classmethod
  #@abstractmethod
  def parse(clazz, text):
    return file_sort_order.parse_string(text)

  @classmethod
  #@abstractmethod
  def check(clazz, value, allow_none = False):
    return check.check_file_sort_order(value, allow_none = allow_none)

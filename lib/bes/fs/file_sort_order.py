#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_type_checked_enum import bcli_type_checked_enum
from bes.enum_util.checked_enum import checked_enum

class file_sort_order(checked_enum):
  DATE = 'date'
  DEPTH = 'depth'
  FILENAME = 'filename'
  SIZE = 'size'

file_sort_order.register_check_class()

class cli_file_sort_order_type(bcli_type_checked_enum):
  __enum_class__ = file_sort_order

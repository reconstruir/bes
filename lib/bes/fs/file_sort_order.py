#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.enum_util.checked_enum import checked_enum

class file_sort_order(checked_enum):
  DATE = 'date'
  DEPTH = 'depth'
  FILENAME = 'filename'
  SIZE = 'size'

file_sort_order.register_check_class()

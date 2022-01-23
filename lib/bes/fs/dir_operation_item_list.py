#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.common.algorithm import algorithm
from bes.common.check import check
from bes.common.type_checked_list import type_checked_list

from .dir_operation_item import dir_operation_item
from .file_path import file_path

class dir_operation_item_list(type_checked_list):

  __value_type__ = dir_operation_item
  
  def __init__(self, values = None):
    super(dir_operation_item_list, self).__init__(values = values)

  def execute_operation(self, timestamp, count):
    for item in self:
      if item.execute_operation(f'{timestamp}-{count}'):
        count += 1
    
check.register_class(dir_operation_item_list, include_seq = False)

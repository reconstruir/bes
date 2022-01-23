#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.enum_util.checked_enum import checked_enum

class dir_operation_item_type(checked_enum):
  MOVE = 'move'
  REMOVE = 'remove'

dir_operation_item_type.register_check_class()

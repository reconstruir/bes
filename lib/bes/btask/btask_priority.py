#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.enum_util.checked_int_enum import checked_int_enum

class btask_priority(checked_int_enum):
  HIGH = 1
  MEDIUM = 2
  LOW = 3

btask_priority.register_check_class()

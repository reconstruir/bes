#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.enum_util.checked_enum import checked_enum

class btask_result_state(checked_enum):
  SUCCESS = 'success'
  CANCELLED = 'cancelled'
  FAILED = 'failed'

btask_result_state.register_check_class()

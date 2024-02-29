#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..enum_util.checked_enum import checked_enum

class btl_comment_position(checked_enum):
  END_OF_LINE = 'end_of_line'
  NEW_LINE = 'new_line'
  START_OF_LINE = 'start_of_line'

btl_comment_position.register_check_class()

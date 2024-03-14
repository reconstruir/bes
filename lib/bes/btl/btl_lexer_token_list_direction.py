#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..enum_util.checked_enum import checked_enum

class btl_lexer_token_list_direction(checked_enum):
  LEFT = -1
  RIGHT = 1

btl_lexer_token_list_direction.register_check_class()

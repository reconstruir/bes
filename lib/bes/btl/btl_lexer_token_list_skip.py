#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..enum_util.checked_enum import checked_enum

class btl_lexer_token_list_skip(checked_enum):
  ONE = '?'
  ONE_OR_MORE = '+'
  ZERO_OR_MORE = '*'

btl_lexer_token_list_skip.register_check_class()

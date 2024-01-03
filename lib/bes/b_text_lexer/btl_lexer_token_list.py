#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import io

from ..common.json_util import json_util
from ..common.type_checked_list import type_checked_list
from ..system.check import check

from .btl_lexer_token import btl_lexer_token

class btl_lexer_token_list(type_checked_list):

  __value_type__ = btl_lexer_token
  
  def __init__(self, values = None):
    super().__init__(values = values)

  def to_source_string(self):
    buf = io.StringIO()
    for token in self:
      buf.write(token.value)
    return buf.getvalue()
  
  def to_dict_list(self):
    return [ item.to_dict() for item in self ]

  def to_json(self):
    return json_util.to_json(self.to_dict_list(), indent = 2, sort_keys = False)
  
btl_lexer_token_list.register_check_class()

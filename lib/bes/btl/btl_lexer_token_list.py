#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import deque

import io

from ..common.json_util import json_util
from ..system.check import check

from .btl_lexer_token import btl_lexer_token

class btl_lexer_token_list(object):

  def __init__(self, values = None):
    self._values = deque()
    for value in (values or []):
      self.append(value)

  def __len__(self):
    return len(self._values)

  def __iter__(self):
    return iter(self._values)

  def append(self, token):
    token = check.check_btl_lexer_token(token)

    self._values.append(token)
  
  def to_source_string(self):
    buf = io.StringIO()
    for token in self:
      buf.write(token.value or '')
    return buf.getvalue()
  
  def to_dict_list(self):
    return [ item.to_dict() for item in self ]

  def to_json(self):
    return json_util.to_json(self.to_dict_list(), indent = 2, sort_keys = False)

  def to_json(self):
    return json_util.to_json(self.to_dict_list(), indent = 2, sort_keys = False)

check.register_class(btl_lexer_token_list, include_seq = False)

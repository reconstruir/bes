#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import deque
from collections import OrderedDict

import io
import json

from ..common.json_util import json_util
from ..system.check import check

from .btl_lexer_token import btl_lexer_token

class btl_lexer_token_deque(object):

  def __init__(self, values = None):
    self._values = deque()
    for value in (values or []):
      self.append(value)

  def __len__(self):
    return len(self._values)

  def __iter__(self):
    return iter(self._values)

  def clear(self):
    self._values = deque()
  
  def append(self, token):
    token = check.check_btl_lexer_token(token)

    self._values.append(token)

  def extend(self, tokens):
    self._values.extend(tokens)

  def prepend(self, token):
    token = check.check_btl_lexer_token(token)

    self._values.appendleft(token)

  def to_ordered_dict(self):
    if not self._values:
      return OrderedDict()
    result = OrderedDict()

    for token in self:
      if token.type_hint == 'h_done':
        continue
      assert token.has_position()
      line_number = token.position.y
      if not line_number in result:
        result[line_number] = btl_lexer_token_deque()
      if token.type_hint != 'h_line_break':
        result[line_number].append(token)
    for line_number, line_list in result.items():
      line_list.sort_by_x()
    return result

  def insert(self):
    pass
    
  def to_source_string(self):
    buf = io.StringIO()
    for token in self:
      buf.write(token.value or '')
    return buf.getvalue()
  
  def to_dict_list(self):
    return [ token.to_dict() for token in self ]

  def to_list(self):
    return [ token for token in self ]

  def sort_by_x(self):
    sorted_values = sorted(self.to_list(), key = lambda token: token.position.x)
    self.clear()
    self.extend(sorted_values)
  
  def to_json(self):
    return json_util.to_json(self.to_dict_list(), indent = 2, sort_keys = False)

  @classmethod
  def parse_dict_list(clazz, l):
    result = btl_lexer_token_deque()
    for token_dict in l:
      token = btl_lexer_token.parse_dict(token_dict)
      result.append(token)
    return result

  @classmethod
  def parse_json(clazz, s):
    check.check_string(s)

    dict_list = json.loads(s)
    return clazz.parse_dict_list(dict_list)
  
check.register_class(btl_lexer_token_deque, include_seq = False)

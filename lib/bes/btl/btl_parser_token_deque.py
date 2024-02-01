#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import deque
from collections import OrderedDict

import io
import json

from ..common.json_util import json_util
from ..system.check import check

from .btl_parser_token import btl_parser_token

class btl_parser_token_deque(object):

  def __init__(self, tokens = None):
    self._tokens = deque()
    for token in (tokens or []):
      self.append(token)

  def __len__(self):
    return len(self._tokens)

  def __iter__(self):
    return iter(self._tokens)

#  def __getitem__(self, subscript):
#    result = self._tokens[subscript]
#    if isinstance(result, btl_parser_token):
#      return result
#    print(type(result))
    
  def clear(self):
    self._tokens = deque()
  
  def append(self, token):
    token = check.check_btl_parser_token(token)

    self._tokens.append(token)

  def extend(self, tokens):
    self._tokens.extend(tokens)

  def prepend(self, token):
    token = check.check_btl_parser_token(token)

    self._tokens.appendleft(token)

  def to_line_break_ordered_dict(self):
    if not self._tokens:
      return OrderedDict()
    result = OrderedDict()

    for token in self:
      if token.type_hint == 'h_done':
        continue
      assert token.has_position()
      line_number = token.position.y
      if not line_number in result:
        result[line_number] = btl_parser_token_deque()
      result[line_number].append(token)
    for line_number, line_list in result.items():
      line_list.sort_by_x()
      
    return result

  def modify_value(self, token_name, new_value):
    check.check_string(token_name)
    check.check_string(new_value, allow_none = True)

    found = False
    x_shift = None
    STATE_BEFORE_FOUND = 1
    STATE_AFTER_FOUND = 2
    state = STATE_BEFORE_FOUND
    for i, token in enumerate(self):
      if state == STATE_BEFORE_FOUND:
        if token.name == token_name:
          found = True
          new_token, x_shift = token.clone_replace_value(new_value)
          assert x_shift != None
          self._tokens[i] = new_token
          state = STATE_AFTER_FOUND
      elif state == STATE_AFTER_FOUND:
        assert x_shift != None
        new_token = token.clone_with_x_shift(x_shift)
        self._tokens[i] = new_token
      else:
        assert False, f'unexpected state {state}'

  def shift_y(self, y_shift):
    check.check_int(y_shift)

    new_tokens = deque()
    for token in self:
      new_token = token.clone_with_y_shift(y_shift)
      new_tokens.append(new_token)
    self._tokens = new_tokens

  def set_y(self, y):
    check.check_int(y)

    new_tokens = deque()
    for token in self:
      new_token = token.clone_with_y(y)
      new_tokens.append(new_token)
    self._tokens = new_tokens
    
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
    sorted_tokens = sorted(self.to_list(), key = lambda token: token.position.x)
    self.clear()
    self.extend(sorted_tokens)
  
  def to_json(self):
    return json_util.to_json(self.to_dict_list(), indent = 2, sort_keys = False)

  @classmethod
  def parse_dict_list(clazz, l):
    result = btl_parser_token_deque()
    for token_dict in l:
      token = btl_parser_token.parse_dict(token_dict)
      result.append(token)
    return result

  @classmethod
  def parse_json(clazz, s):
    check.check_string(s)

    dict_list = json.loads(s)
    return clazz.parse_dict_list(dict_list)
  
check.register_class(btl_parser_token_deque, include_seq = False)

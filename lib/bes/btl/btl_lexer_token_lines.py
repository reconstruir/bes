#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import deque

import io
import json

from ..common.json_util import json_util
from ..system.check import check

from .btl_lexer_token import btl_lexer_token
from .btl_lexer_token_deque import btl_lexer_token_deque

class _lexer_token_line(object):

  def __init__(self, line_number, tokens):
    self.line_number = line_number
    self.tokens = tokens

class btl_lexer_token_lines(object):

  def __init__(self, tokens):
    check.check_btl_lexer_token_deque(tokens)
    
    self._lines = deque()
    d = tokens.to_line_break_ordered_dict()
    for line_number, tokens in d.items():
      line = _lexer_token_line(line_number, tokens)
      self._lines.append(line)

  def __len__(self):
    return len(self._lines)

  def __iter__(self):
    for line in self._lines:
      for token in line.tokens:
        yield token

  def clear(self):
    self._lines = deque()
  
#  def append(self, token):
#    token = check.check_btl_lexer_token(token)
#
#    self._values.append(token)
#
#  def extend(self, tokens):
#    self._values.extend(tokens)
#
#  def prepend(self, token):
#    token = check.check_btl_lexer_token(token)
#
#    self._values.appendleft(token)
#

  def insert(self):
    pass
    
  def to_source_string(self):
    buf = io.StringIO()
    for token in self:
      buf.write(token.value or '')
    return buf.getvalue()
  
#  def to_dict_list(self):
#    return [ token.to_dict() for token in self ]
#
#  def to_list(self):
#    return [ token for token in self ]
#
#  def sort_by_x(self):
#    sorted_values = sorted(self.to_list(), key = lambda token: token.position.x)
#    self.clear()
#    self.extend(sorted_values)
#  
#  def to_json(self):
#    return json_util.to_json(self.to_dict_list(), indent = 2, sort_keys = False)
#
#  @classmethod
#  def parse_dict_list(clazz, l):
#    result = btl_lexer_token_deque()
#    for token_dict in l:
#      token = btl_lexer_token.parse_dict(token_dict)
#      result.append(token)
#    return result
#
#  @classmethod
#  def parse_json(clazz, s):
#    check.check_string(s)
#
#    dict_list = json.loads(s)
#    return clazz.parse_dict_list(dict_list)
  
check.register_class(btl_lexer_token_lines, include_seq = False)

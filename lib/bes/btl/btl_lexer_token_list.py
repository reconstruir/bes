#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from collections import OrderedDict

import io
import json
import os

from ..common.json_util import json_util
from ..common.type_checked_list import type_checked_list
from ..system.check import check

from .btl_lexer_token import btl_lexer_token

class btl_lexer_token_list(type_checked_list):

  __value_type__ = btl_lexer_token
  
  def to_line_break_ordered_dict(self):
    if not self._values:
      return OrderedDict()
    result = OrderedDict()

    for token in self:
      if token.type_hint == 'h_done':
        continue
      assert token.has_position()
      line = token.position.line
      if not line in result:
        result[line] = btl_lexer_token_list()
      result[line].append(token)
    for line, line_list in result.items():
      line_list.sort_by_column()
      
    return result

  def modify_value(self, token_name, new_value):
    check.check_string(token_name)
    check.check_string(new_value, allow_none = True)

    found = False
    column_delta = None
    STATE_BEFORE_FOUND = 1
    STATE_AFTER_FOUND = 2
    state = STATE_BEFORE_FOUND
    for i, token in enumerate(self):
      if state == STATE_BEFORE_FOUND:
        if token.name == token_name:
          found = True
          column_delta = token.replace_value(new_value)
          assert column_delta != None
          state = STATE_AFTER_FOUND
      elif state == STATE_AFTER_FOUND:
        assert column_delta != None
        token.move_horizontal(column_delta)
      else:
        assert False, f'unexpected state {state}'

  def shift_vertical(self, line_delta):
    check.check_int(line_delta)

    for token in self:
      token.move_vertical(line_delta)

  def set_line(self, line):
    check.check_int(line)

    for token in self:
      token.move_to_line(line)
    
  def to_source_string(self):
    buf = io.StringIO()
    for token in self:
      buf.write(token.value or '')
    return buf.getvalue()
  
  def to_dict_list(self):
    return [ token.to_dict() for token in self ]

  def sort_by_column(self):
    sorted_tokens = sorted(self.to_list(), key = lambda token: token.position.column)
    self.clear()
    self.extend(sorted_tokens)
  
  def to_json(self):
    return json_util.to_json(self.to_dict_list(), indent = 2, sort_keys = False)

  @classmethod
  def parse_dict_list(clazz, l):
    result = btl_lexer_token_list()
    for token_dict in l:
      token = btl_lexer_token.parse_dict(token_dict)
      result.append(token)
    return result

  @classmethod
  def parse_json(clazz, s):
    check.check_string(s)

    dict_list = json.loads(s)
    return clazz.parse_dict_list(dict_list)

  def find_index_backwards(self, index, func, negate = False, raise_error = False, error_message = None):
    check.check_int(index)
    check.check_callable(func)
    check.check_bool(negate)
    check.check_bool(raise_error)
    check.check_string(error_message, allow_none = True)

    if index < 0:
      index = len(self._values) + index + 1
    for next_index in reversed(range(0, index + 1)):
      next_token = self[next_index]
      func_result = func(next_token)
      if negate:
        nc_result = not nc_result
      if func_result:
        return next_index
    if raise_error:
      raise IndexError(self._make_find_index_error_message(index, error_message))
    return -1

  def find_index_forwards(self, index, func, negate = False, raise_error = False, error_message = None):
    check.check_int(index)
    check.check_callable(func)
    check.check_bool(raise_error)
    check.check_bool(negate)
    check.check_string(error_message, allow_none = True)
    
    if index < 0:
      index = len(self._values) + index + 1
    for next_index in range(index + 0, len(self)):
      next_token = self[next_index]
      func_result = func(next_token)
      if negate:
        nc_result = not nc_result
      if func_result:
        return next_index
    if raise_error:
      raise IndexError(self._make_find_index_error_message(index, error_message))
    return -1
  
  def find_backwards(self, index, func, negate = False, raise_error = False, error_message = None):
    found_index = self.find_index_backwards(index,
                                            func,
                                            negate = negate,
                                            raise_error = raise_error,
                                            error_message = error_message)
    return None if found_index < 0 else self[found_index]

  def find_forwards(self, index, func, negate = False, raise_error = False, error_message = None):
    found_index = self.find_index_forwards(index,
                                           func,
                                           negate = negate,
                                           raise_error = raise_error,
                                           error_message = error_message)
    return None if found_index < 0 else self[found_index]

  @classmethod
  def _make_token_names_set(clazz, token_name):
    if check.is_string(token_name):
      token_names = set([ token_name ])
    else:
      token_names = set([ t for t in token_name ])
    return token_names
  
  def find_index_backwards_by_name(self, index, token_name, negate = False, raise_error = False, error_message = None):
    token_names = self._make_token_names_set(token_name)
    return self.find_index_backwards(index,
                                     lambda token: token.name in token_names,
                                     negate = negate,
                                     raise_error = raise_error,
                                     error_message = error_message)

  def find_index_forwards_by_name(self, index, token_name, negate = False, raise_error = False, error_message = None):
    token_names = self._make_token_names_set(token_name)
    return self.find_index_forwards(index,
                                    lambda token: token.name in token_names,
                                    negate = negate,
                                    raise_error = raise_error,
                                    error_message = error_message)

  def find_backwards_by_name(self, index, token_name, negate = False, raise_error = False, error_message = None):
    found_index = self.find_index_backwards_by_name(index,
                                                    token_name,
                                                    negate = negate,
                                                    raise_error = raise_error,
                                                    error_message = error_message)
    return None if found_index < 0 else self[found_index]

  def find_forwards_by_name(self, index, token_name, negate = False, raise_error = False, error_message = None):
    found_index = self.find_index_forwards_by_name(index,
                                                   token_name,
                                                   negate = negate,
                                                   raise_error = raise_error,
                                                   error_message = error_message)
    return None if found_index < 0 else self[found_index]
  
  def find_backwards_by_line(self, index, line, negate = False, raise_error = False, error_message = None):
    return self.find_backwards(index,
                               lambda token: token.position.line == line,
                               negate = negate,
                               raise_error = raise_error,
                               error_message = error_message)

  def find_forwards_by_line(self, index, line, negate = False, raise_error = False, error_message = None):
    return self.find_forwards(index,
                              lambda token: token.position.line == line,
                              negate = negate,
                              raise_error = raise_error,
                              error_message = error_message)

  def skip_index_forwards(self, index, token_name, num, negate = False, raise_error = False, error_message = None):
    check.check_int(num)
    
    if index < 0:
      index = len(self._values) + index + 1
    token_names = self._make_token_names_set(token_name)
    tokens = self._values[index:]
    next_index = index
    last_index = -1
    count = 0
    for token in tokens:
      name_result = token.name in token_names
      if negate:
        name_result = not name_result
      if name_result:
        count += 1
        if num > 0 and count == num:
          return next_index
      else:
        if num < 0:
          return last_index
        return -1
      last_index = next_index
      next_index += 1
    return -1
  
  @classmethod
  def _make_find_index_error_message(clazz, index, error_message):
    msg = f'Token not found from index {index}'
    if error_message:
      msg = msg + ': ' + error_message
    return msg

  @classmethod
  def _make_find_line_error_message(clazz, line, error_message):
    msg = f'Token not found from line {line}'
    if error_message:
      msg = msg + ': ' + error_message
    return msg
  
  def to_debug_str(self):
    max_index_length = len(str(len(self) - 1))
    return os.linesep.join([ f'{i:>{max_index_length}}: {token.to_debug_str()}' for i, token in enumerate(self) ])

  def first_line_to_index(self, line, raise_error = False, error_message = None):
    check.check_int(line)
    check.check_bool(raise_error)
    check.check_string(error_message, allow_none = True)

    index = self._bisect_by_line(line)
    if index < 0:
      if raise_error:
        raise IndexError(self._make_find_line_error_message(line, error_message))

    result = -1
    for next_index in reversed(range(0, index + 1)):
      next_token = self._values[next_index]
      if next_token.position and next_token.position.line == line:
        result = next_index
      else:
        break
    return result

  def last_line_to_index(self, line, raise_error = False, error_message = None):
    check.check_int(line)
    check.check_bool(raise_error)
    check.check_string(error_message, allow_none = True)

    index = self._bisect_by_line(line)
    if index < 0:
      if raise_error:
        raise IndexError(self._make_find_line_error_message(line, error_message))

    result = -1
    for next_index in range(index, len(self)):
      next_token = self._values[next_index]
      if next_token.position and next_token.position.line == line:
        result = next_index
      else:
        break
    return result
  
  def _bisect_by_line(self, line):
    left = 0
    right = len(self._values) - 1

    while left <= right:
      mid = (left + right) // 2
      mid_val = self._values[mid]
      mid_val_line = mid_val.position.line
      if mid_val_line == line:
        return mid
      elif mid_val_line < line:
        left = mid + 1
      else:
        right = mid - 1
    return -1

  def dump(self, label):
    check.check_string(label)

    print(label)
    print(self.to_debug_str())

btl_lexer_token_list.register_check_class()  

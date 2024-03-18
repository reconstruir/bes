#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from collections import OrderedDict
from collections.abc import Iterator

import io
import json
import os

from ..common.json_util import json_util
from ..system.log import logger
from ..common.type_checked_list import type_checked_list
from ..system.check import check

from .btl_lexer_token import btl_lexer_token
from .btl_lexer_token_list_direction import btl_lexer_token_list_direction
from .btl_lexer_token_list_skip import btl_lexer_token_list_skip

class btl_lexer_token_list(type_checked_list):

  __value_type__ = btl_lexer_token

  _log = logger('btl_lexer_token_list')
  @property
  def first_line(self):
    for token in self:
      if token.name != 't_done':
        return token.position.line
    return None

  @property
  def last_line(self):
    for token in reversed(self):
      if token.name != 't_done':
        return token.position.line
    return None
  
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

  @classmethod
  def _call_func(clazz, label, func, token, negate):
    func_result = func(token)
    if negate:
      func_result = not func_result
    #self._log.log_d(f'{label}: func_result={func_result}')
    return func_result

  _iter_item = namedtuple('_iter_item', 'token, func_result, current_index, last_index, next_index')
  @classmethod
  def _call_iter(clazz, label, tokens, direction, func, negate):
    for token in tokens:
      current_index = token.index
      last_index = current_index - direction.value
      next_index = current_index + direction.value
      func_result = clazz._call_func(label, func, token, negate)
      clazz._log.log_d(f'{label}: func_result={func_result} current_index={current_index} last_index={last_index} next_index={next_index} token={token.to_debug_str()}')
      item = clazz._iter_item(token, func_result, current_index, last_index, next_index)
      yield item
    
  def _skip_index_iter_one(self, label, tokens, direction, func, negate):
    for item in self._call_iter(label, tokens, direction, func, negate):
      if item.func_result:
        return item.next_index
      else:
        break
    return -1

  def _skip_index_iter_zero_or_one(self, label, tokens, direction, func, negate):
    for item in self._call_iter(label, tokens, direction, func, negate):
      if item.func_result:
        return item.next_index
      else:
        return item.current_index
    return -1

  def _skip_index_iter_zero_or_more(self, label, tokens, direction, func, negate):
    assert len(tokens) > 0
    result = -1
    for item in self._call_iter(label, tokens, direction, func, negate):
      if item.func_result:
        result = item.next_index
      else:
        return item.current_index
    assert result != -1
    return result

  def _skip_index_iter_one_or_more(self, label, tokens, direction, func, negate):
    for item in self._call_iter(label, tokens, direction, func, negate):
      if not item.func_result:
        return item.current_index
    return item.next_index

  def skip_index(self, starting_index, direction, func, skip,
                 negate = False, label = None):
    check.check_int(starting_index)
    direction = check.check_btl_lexer_token_list_direction(direction)
    check.check_callable(func)
    skip = check.check_btl_lexer_token_list_skip(skip)
    check.check_bool(negate)
    check.check_string(label, allow_none = True, default_value = 'skip_index')

    self._log.log_d(f'{label}: starting_index={starting_index} direction={direction.name} skip={skip.name}')
    
    if starting_index < 0:
      starting_index = len(self._values) + starting_index + 1
    if direction == direction.RIGHT:
      tokens = btl_lexer_token_list(self._values[starting_index:])
    else:
      tokens = btl_lexer_token_list([ n for n in reversed(self._values[0:starting_index + 1]) ])

    self._log.log_d(f'{label}: self.tokens:\n{self.to_debug_str()}', multi_line = True)
    self._log.log_d(f'{label}: tokens for skip:\n{tokens.to_debug_str()}', multi_line = True)
      
    m = {
      skip.ONE: self._skip_index_iter_one,
      skip.ZERO_OR_ONE: self._skip_index_iter_zero_or_one,
      skip.ZERO_OR_MORE: self._skip_index_iter_zero_or_more,
      skip.ONE_OR_MORE: self._skip_index_iter_one_or_more,
    }
    result = m[skip](label, tokens, direction, func, negate)
    self._log.log_d(f'{label}: result={result}')
    return result
  
  def skip_index_by_name(self, starting_index, direction, token_name, skip,
                         negate = False, label = None):
    token_names = self._make_token_names_set(token_name)
    return self.skip_index(starting_index,
                           direction,
                           lambda token: token.name in token_names,
                           skip,
                           negate = negate,
                           label = 'skip_index_by_name')
  
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
    s = os.linesep.join([ f'{i:>{max_index_length}}: {token.to_debug_str()}' for i, token in enumerate(self) ])
    return s + os.linesep

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

    if line < 0:
      line = self.last_line + line + 1
    
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

  def reorder(self, delta_line, starting_index):
    check.check_int(delta_line)
    check.check_int(starting_index)

    for token in self:
      token.index = starting_index
      starting_index += 1
      if delta_line and token.position:
        token.position = token.position.moved_vertical(delta_line)

  def count_lines(self):
    lines = set()
    for token in self:
      if token.position:
        lines.add(token.position.line)
    return len(lines)

  def insert_token(self, index, token):
    check.check_int(index)
    token = check.check_btl_lexer_token(token)

    return self.insert_tokens(index, [ token ])

  def insert_tokens(self, index, new_tokens):
    check.check_int(index)
    new_tokens = check.check_btl_lexer_token_list(new_tokens)

    self._log.log_d(f'insert_tokens: index={index} new_tokens:\n{new_tokens.to_debug_str()}', multi_line = True)
    self._log.log_d(f'insert_tokens: tokens before:\n{self.to_debug_str()}', multi_line = True)
    top, bottom = self.partition_for_insert(index)

    new_tokens_line_delta = top.last_line
    if new_tokens_line_delta == None:
      new_tokens_line_delta = 0
    new_tokens_starting_index = len(top) + 0
    self._log.log_d(f'insert_tokens: new_tokens_line_delta={new_tokens_line_delta} new_tokens_starting_index={new_tokens_starting_index}')
    new_tokens.reorder(new_tokens_line_delta, new_tokens_starting_index)

    if bottom.first_line:
      bottom_line_delta = new_tokens.last_line - bottom.first_line + 1
    else:
      bottom_line_delta = new_tokens.last_line + 1
    bottom_starting_index = len(top) + len(new_tokens) + 0
    self._log.log_d(f'insert_tokens: bottom_line_delta={bottom_line_delta} bottom_starting_index={bottom_starting_index}')
    bottom.reorder(bottom_line_delta, bottom_starting_index)

    self._values = top + new_tokens + bottom
    self._log.log_d(f'insert_tokens: tokens after:\n{self.to_debug_str()}')
    return index

btl_lexer_token_list.register_check_class()  

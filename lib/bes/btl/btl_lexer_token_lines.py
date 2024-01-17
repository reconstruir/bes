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

  def clone_with_y(self, y):
    check.check_int(y)

    new_line_number = self.line_number + 1
    new_line = _lexer_token_line(new_line_number, self.tokens)
    new_line.tokens.set_y(new_line_number)
    return new_line
        
class btl_lexer_token_lines(object):

  def __init__(self, tokens):
    check.check_btl_lexer_token_deque(tokens)
    
    self._lines = deque()
    self._indeces = {}
    d = tokens.to_line_break_ordered_dict()
    for line_number, tokens in d.items():
      line = _lexer_token_line(line_number, tokens)
      self._lines.append(line)
      assert line_number not in self._indeces
      self._indeces[line_number] = line

  def __len__(self):
    return len(self._lines)

  def __iter__(self):
    for line in self._lines:
      for token in line.tokens:
        yield token

  def clear(self):
    self._lines = deque()

  def modify_value(self, line_number, token_name, new_value):
    check.check_int(line_number)
    check.check_string(token_name)
    check.check_string(new_value, allow_none = True)

    assert line_number in self._indeces
    line = self._indeces[line_number]
    line.tokens.modify_value(token_name, new_value)
    
  def insert_line(self, line_number, tokens):
    check.check_int(line_number)
    check.check_btl_lexer_token_deque(tokens)
    
    STATE_BEFORE_FOUND = 1
    STATE_AFTER_FOUND = 2
    state = STATE_BEFORE_FOUND
    new_lines = deque()
    
    for line in self._lines:
      if state == STATE_BEFORE_FOUND:
        if line.line_number == line_number:
          found = True
          tokens.set_y(line_number)
          new_line = _lexer_token_line(line_number, tokens)
          new_lines.append(new_line)

          old_line = line.clone_with_y(line.line_number + 1)
          new_lines.append(old_line)
          
          state = STATE_AFTER_FOUND
        else:
          new_lines.append(line)
      elif state == STATE_AFTER_FOUND:
        new_line = line.clone_with_y(line.line_number + 1)
        new_lines.append(new_line)
      else:
        assert False, f'unexpected state {state}'
    if state == STATE_BEFORE_FOUND:
      tokens.set_y(line_number)
      new_line = _lexer_token_line(line_number, tokens)
      new_lines.append(new_line)
      
    self._lines = new_lines
    self._indeces = {}
    for line in self._lines:
      assert line.line_number not in self._indeces
      self._indeces[line.line_number] = line
    
  def to_source_string(self):
    buf = io.StringIO()
    for token in self:
      buf.write(token.value or '')
    return buf.getvalue()
  
check.register_class(btl_lexer_token_lines, include_seq = False)

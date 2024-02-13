#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import deque

import io
import json

from ..common.json_util import json_util
from ..system.check import check

from .btl_lexer_token import btl_lexer_token
from .btl_lexer_token_deque import btl_lexer_token_deque
  
class btl_lexer_token_lines(object):

  class _item(object):

    def __init__(self, line, tokens):
      self.line = line
      self.tokens = tokens

    def clone_moved_to_line(self, line):
      check.check_int(line)

      new_item = self.__class__(line, self.tokens)
      new_item.tokens.set_line(line)
      return new_item

    def to_dict(self):
      return {
        'line': self.line,
        'tokens': self.tokens.to_dict_list(),
      }
  
  def __init__(self, tokens):
    check.check_btl_lexer_token_deque(tokens)
    
    self._items = deque()
    self._indeces = {}
    self._first_line = None
    self._last_line = None
    d = tokens.to_line_break_ordered_dict()
    for line, tokens in d.items():
      item = self._item(line, tokens)
      self._items.append(item)
      assert line not in self._indeces
      self._indeces[line] = item
      if self._last_line == None:
        self._first_line = line
        self._last_line = line
      else:
        self._first_line = min(self._first_line, line)
        self._last_line = max(self._last_line, line)

  def __len__(self):
    return len(self._items)

  def __iter__(self):
    for item in self._items:
      for token in item.tokens:
        yield token

  def to_dict_list(self):
    return [ item.to_dict() for item in self._items ]

  def to_json(self):
    return json_util.to_json(self.to_dict_list(), indent = 2, sort_keys = False)
  
  def clear(self):
    self._items = deque()

  def modify_value(self, line, token_name, new_value):
    check.check_int(line)
    check.check_string(token_name)
    check.check_string(new_value, allow_none = True)

    assert line in self._indeces
    item = self._indeces[line]
    item.tokens.modify_value(token_name, new_value)
    
  def insert_line(self, line, tokens):
    check.check_int(line)
    check.check_btl_lexer_token_deque(tokens)
    
    STATE_BEFORE_FOUND = 1
    STATE_AFTER_FOUND = 2
    state = STATE_BEFORE_FOUND
    new_items = deque()
    
    for item in self._items:
      if state == STATE_BEFORE_FOUND:
        if item.line == line:
          found = True
          tokens.set_line(line)
          new_item = self._item(line, tokens)
          new_items.append(new_item)

          old_line = item.clone_moved_to_line(item.line + 1)
          new_items.append(old_line)
          
          state = STATE_AFTER_FOUND
        else:
          new_items.append(item)
      elif state == STATE_AFTER_FOUND:
        new_item = item.clone_moved_to_line(item.line + 1)
        new_items.append(new_item)
      else:
        assert False, f'unexpected state {state}'
    # we did not find line so we are at the end
    if state == STATE_BEFORE_FOUND:
      tokens.set_line(line)
      new_item = self._item(line, tokens)
      new_items.append(new_item)
      
    self._items = new_items

    # renumber the indeces
    self._indeces = {}
    self._first_line = None
    self._last_line = None
    for item in self._items:
      line = item.line
      assert line not in self._indeces
      self._indeces[line] = item
      if self._last_line == None:
        self._first_line = line
        self._last_line = line
      else:
        self._first_line = min(self._first_line, line)
        self._last_line = max(self._last_line, line)

  def to_source_string(self):
    buf = io.StringIO()
    for token in self:
      buf.write(token.value or '')
    return buf.getvalue()

check.register_class(btl_lexer_token_lines, include_seq = False)

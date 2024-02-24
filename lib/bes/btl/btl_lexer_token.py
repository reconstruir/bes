#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy
import os

from collections import namedtuple

from ..common.json_util import json_util
from ..common.tuple_util import tuple_util
from ..system.check import check
from ..text.line_numbers import line_numbers

from .btl_debug import btl_debug
from .btl_document_position import btl_document_position

class btl_lexer_token(namedtuple('btl_lexer_token', 'name, value, position, type_hint, index')):

  def __new__(clazz, name = None, value = None, position = ( 1, 1 ), type_hint = None, index = None):
    check.check_string(name)
    check.check_string(value, allow_none = True)
    position = check.check_btl_document_position(position, allow_none = True)
    check.check_string(type_hint, allow_none = True)
    check.check_int(index, allow_none = True)
    
    return clazz.__bases__[0].__new__(clazz, name, value, position, type_hint, index)

  def __str__(self):
    parts = [
      self.name, 
      self.value or '', 
      f'p={self.position}' if self.position != None else None,      
      f'h={self.type_hint}' if self.type_hint != None else None,      
      f'i={self.index}' if self.index != None else None,
    ]
    return ':'.join([ str(part) for part in parts if part != None ])

  def to_dict(self):
    return {
      'name': self.name,
      'value': self.value,
      'position': str(self.position or ''),
      'type_hint': self.type_hint,
      'index': self.index,
    }

  @classmethod
  def parse_dict(clazz, d):
    assert 'name' in d
    assert 'value' in d
    assert 'position' in d
    assert 'type_hint' in d

    name = d['name']
    value = d['value']
    position = d['position']
    type_hint = d['type_hint']
    index = d.get('index', None)
    return btl_lexer_token(name,
                           value,
                           btl_document_position.parse_str(position) if position else None,
                           type_hint,
                           index)
  
  def has_position(self):
    return self.position != None
  
  def to_json(self):
    return json_util.to_json(self.to_dict(), indent = 2, sort_keys = False)
  
  def clone(self, mutations = None):
    mutations = mutations or {}
    if 'position' in mutations:
      position = mutations['position']
      position = check.check_btl_document_position(position, allow_none = True)
    else:
      position = self.position
    copied_mutations = copy.deepcopy(mutations)
    if position == None:
      cloned_position = None
    else:
      cloned_position = position.clone()
    copied_mutations['position'] = cloned_position
    return tuple_util.clone(self, mutations = copied_mutations)

  def clone_replace_value(self, new_value):
    check.check_string(new_value)
    
    old_length = len(self.value)
    new_length = len(new_value)
    horizontal_shift = new_length - old_length
    new_token = self.clone(mutations = { 'value': new_value })
    return new_token, horizontal_shift

  def clone_replace_index(self, new_index):
    check.check_int(new_index, allow_none = True)
    
    return self.clone(mutations = { 'index': new_index })
  
  def clone_with_moved_horizontal(self, horizontal_delta):
    check.check_int(horizontal_delta)

    return self.clone(mutations = { 'position': self.position.moved_horizontal(horizontal_delta) })

  def clone_with_moved_vertical(self, vertical_delta):
    check.check_int(vertical_delta)

    return self.clone(mutations = { 'position': self.position.moved_vertical(vertical_delta) })

  def clone_moved_to_line(self, line):
    check.check_int(line)
    
    return self.clone(mutations = { 'position': self.position.moved_to_line(line) })

  def to_debug_str(self):
    debug_value = self.make_debug_str(self.value)
    debug_token = self.clone(mutations = { 'value': debug_value })
    return str(debug_token)

  @classmethod
  def make_debug_str(clazz, s):
    return btl_debug.make_debug_str(s)
  
  @classmethod
  def _check_cast_func(clazz, obj):
    return tuple_util.cast_seq_to_namedtuple(clazz, obj)

  def make_error_text(self, text, message):
    check.check_string(text)
    check.check_string(message)

    if not text:
      return ''

    NUM_CONTEXT_LINES = 5

    position = self.position or btl_document_position(666, 666)
    
    numbered_text = line_numbers.add_line_numbers(text, delimiter = '|')
    delim_col = numbered_text.find('|')
    lines = numbered_text.splitlines()
    top = lines[0:position.line][-NUM_CONTEXT_LINES:]
    bottom = lines[position.line:][0:NUM_CONTEXT_LINES]
    indent = ' ' * (position.column + delim_col)
    marker = f'{indent}^^^ {message}'
    error_lines = top + [ marker ] + bottom
    return os.linesep.join(error_lines).rstrip()

  @classmethod
  def parse_str(clazz, s):
    parts = s.split(':')

    assert len(parts) > 0
    name = parts.pop(0)
    value = parts.pop(0) if len(parts) else None
    position = None
    type_hint = None
    index = None
    for part in parts:
      left, right = clazz._parse_str_part(part)
      if left == 'p':
        position = right
      elif left == 'i':
        index = right
      elif left == 'h':
        type_hint = right
    return btl_lexer_token(name, value, position, type_hint, index)

  @classmethod
  def _parse_str_part(clazz, part):
    if not part:
      return None
    left, delimiter, right = part.partition('=')
    if left == 'p':
      return left, btl_document_position.parse_str(right)
    elif left == 'h':
      return left, right
    elif left == 'i':
      return left, int(right)
      
check.register_class(btl_lexer_token, include_seq = False, cast_func = btl_lexer_token._check_cast_func)
  

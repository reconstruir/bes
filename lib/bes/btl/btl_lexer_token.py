#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os

from ..common.json_util import json_util
from ..system.check import check
from ..text.line_numbers import line_numbers
from ..compat.cmp import cmp

from .btl_debug import btl_debug
from .btl_document_position import btl_document_position

class btl_lexer_token(object):

  def __init__(self, name = None, value = None, position = ( 1, 1 ), type_hint = None, index = None, node = None):
    check.check_string(name)
    check.check_string(value, allow_none = True)
    position = check.check_btl_document_position(position, allow_none = True)
    check.check_string(type_hint, allow_none = True)
    check.check_int(index, allow_none = True)
    from .btl_parser_node import btl_parser_node
    check.check_btl_parser_node(node, allow_none = True)

    self._name = name
    self._value = value
    self._position = position
    self._type_hint = type_hint
    self._index = index
    self._node = index

  def to_tuple(self):
    return ( self.name, self.value, self.position, self.type_hint, self.index, self.node )

  def __eq__(self, other):
    if other == None:
      return False
    return self.compare(other) == 0

  def __ne__(self, other):
    return self.compare(other) != 0

  def __lt__(self, other):
    return self.compare(other) < 0

  def __le__(self, other):
    return self.compare(other) <= 0

  def __gt__(self, other):
    return self.compare(other) > 0

  def __ge__(self, other):
    return self.compare(other) >= 0

  def compare(self, other):
    other = check.check_btl_lexer_token(other)

    return cmp(self.to_tuple(), other.to_tuple())
  
  @property
  def name(self):
    return self._name

  @property
  def value(self):
    return self._value

  @value.setter
  def value(self, value):
    check.check_string(value, allow_none = True)
    
    self._value = value
  
  @property
  def position(self):
    return self._position

  @position.setter
  def position(self, position):
    position = check.check_btl_document_position(position, allow_none = True)
    
    self._position = position
  
  @property
  def type_hint(self):
    return self._type_hint

  @property
  def index(self):
    return self._index

  @index.setter
  def index(self, index):
    check.check_int(index, allow_none = True)
    
    self._index = index

  @property
  def node(self):
    return self._node
    
  def __eq__(self, other):
    if isinstance(other, btl_lexer_token):
      return self._name == other._name and self._value == other._value and self._position == other._position and self._type_hint == other._type_hint and self._index == other._index
    elif isinstance(other, ( tuple, list )):
      other = self._check_cast_func(other)
      return self._name == other._name and self._value == other._value and self._position == other._position and self._type_hint == other._type_hint and self._index == other._index

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

  def replace_value(self, new_value):
    check.check_string(new_value)
    
    old_length = len(self.value)
    new_length = len(new_value)
    horizontal_shift = new_length - old_length
    self.value = new_value
    return horizontal_shift
  
  def move_horizontal(self, horizontal_delta):
    check.check_int(horizontal_delta)

    self.position = self.position.moved_horizontal(horizontal_delta)
  
  def move_vertical(self, vertical_delta):
    check.check_int(vertical_delta)

    self.position = self.position.moved_vertical(vertical_delta)
  
  def move_to_line(self, line):
    check.check_int(line)
    
    self.position = self.position.moved_to_line(line)
  
  def to_debug_str(self):
    debug_value = self.make_debug_str(self.value)
    debug_token = btl_lexer_token(name = self.name,
                                  value = debug_value,
                                  position = self.position,
                                  type_hint = self.type_hint,
                                  index = self.index)
    return str(debug_token)

  @classmethod
  def make_debug_str(clazz, s):
    return btl_debug.make_debug_str(s)
  
  @classmethod
  def _check_cast_func(clazz, obj):
    if isinstance(obj, ( tuple, list )):
      l = list(obj)[:]
      name = l.pop(0) if l else None
      value = l.pop(0) if l else None
      position = l.pop(0) if l else None
      type_hint = l.pop(0) if l else None
      index = l.pop(0) if l else None
      return btl_lexer_token(name = name,
                             value = value,
                             position = position,
                             type_hint = type_hint,
                             index = index)
    else:
      raise ValueError(f'cannot cast "{obj}" to btl_lexer_token')

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
  

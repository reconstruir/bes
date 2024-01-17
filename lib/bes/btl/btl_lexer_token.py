#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy

from collections import namedtuple

from ..common.json_util import json_util
from ..common.point import point
from ..common.tuple_util import tuple_util
from ..system.check import check

class btl_lexer_token(namedtuple('btl_lexer_token', 'name, value, position, type_hint')):

  def __new__(clazz, name = None, value = None, position = point(1, 1), type_hint = None):
    check.check_string(name)
    check.check_string(value, allow_none = True)
    position = check.check_point(position, allow_none = True)
    check.check_string(type_hint, allow_none = True)
    
    return clazz.__bases__[0].__new__(clazz, name, value, position, type_hint)

  def __str__(self):
    parts = [
      self.name, 
      self.value or '', 
      self.position or '', 
      self.type_hint or None,
    ]
    return ':'.join([ str(part) for part in parts if part != None ])

  def to_dict(self):
    return {
      'name': self.name,
      'value': self.value,
      'position': str(self.position or ''),
      'type_hint': self.type_hint,
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
    return btl_lexer_token(name,
                           value,
                           point.parse_str(position) if position else None,
                           type_hint)
  
  def has_position(self):
    return self.position != None
  
  def to_json(self):
    return json_util.to_json(self.to_dict(), indent = 2, sort_keys = False)
  
  def clone(self, mutations = None):
    mutations = mutations or {}
    if 'position' in mutations:
      position = mutations['position']
      position = check.check_point(position)
    else:
      position = self.position
    copied_mutations = copy.deepcopy(mutations)
    copied_mutations['position'] = position.clone()
    return tuple_util.clone(self, mutations = copied_mutations)

  def clone_replace_value(self, new_value):
    check.check_string(new_value)
    
    old_length = len(self.value)
    new_length = len(new_value)
    x_shift = new_length - old_length
    new_token = self.clone(mutations = { 'value': new_value })
    return new_token, x_shift

  def clone_with_x_shift(self, x_shift):
    check.check_int(x_shift)

    new_position = point(self.position.x + x_shift, self.position.y)
    return self.clone(mutations = { 'position': new_position })
  
  @classmethod
  def _check_cast_func(clazz, obj):
    return tuple_util.cast_seq_to_namedtuple(clazz, obj)
  
check.register_class(btl_lexer_token, include_seq = False, cast_func = btl_lexer_token._check_cast_func)
  

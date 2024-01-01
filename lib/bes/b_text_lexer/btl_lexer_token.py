#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy

from collections import namedtuple

from ..common.json_util import json_util
from ..common.point import point
from ..common.tuple_util import tuple_util
from ..system.check import check

class btl_lexer_token(namedtuple('btl_lexer_token', 'name, value, position')):

  def __new__(clazz, name = None, value = None, position = point(1, 1)):
    check.check_string(name)
    check.check_string(value)
    position = check.check_point(position)
    
    return clazz.__bases__[0].__new__(clazz, name, value, position)

  def __str__(self):
    return f'{self.name}:{self.value}:{self.position}'

  def to_dict(self):
    return {
      'name': self.name,
      'value': self.value,
      'position': str(self.position),
    }

  def to_json(self):
    return json_util.to_json(self.to_dict(), indent = 2, sort_keys = False)
  
  def clone(self, mutations = None):
    mutations = mutations or {}
    if 'position' in mutations:
      position = mutations['position']
      check.check_point(position)
    else:
      position = self.position
    copied_mutations = copy.deepcopy(mutations)
    copied_mutations['position'] = position.clone()
    return tuple_util.clone(self, mutations = copied_mutations)

  @classmethod
  def _check_cast_func(clazz, obj):
    return tuple_util.cast_seq_to_namedtuple(clazz, obj)
  
check.register_class(btl_lexer_token, include_seq = False, cast_func = btl_lexer_token._check_cast_func)
  

#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy

from collections import namedtuple

from bes.common.point import point
from bes.common.tuple_util import tuple_util

class bc_ini_lexer_token(namedtuple('bc_ini_lexer_token', 'token_type, value, position')):

  def __new__(clazz, token_type = None, value = None, position = point(1, 1)):
    return clazz.__bases__[0].__new__(clazz, token_type, value, position)

  def __str__(self):
    return f'{self.token_type},{self.value},{self.position}'

  def __repr__(self):
    return str(self)
  
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

#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from ..common.tuple_util import tuple_util
from ..system.check import check

class point(namedtuple('point', 'x, y')):

  def __new__(clazz, x = None, y = None):
    check.check_int(x, allow_none = True)
    check.check_int(y, allow_none = True)

    x = x or 0
    y = y or 0
    return clazz.__bases__[0].__new__(clazz, x, y)

  def __str__(self):
    return f'{self.x},{self.y}'

  def to_dict(self):
    return dict(self._asdict())
  
  def move(self, delta_x, delta_y):
    return point(self.x + delta_x, self.y + delta_y)

  def clone(self, mutations = None):
    return tuple_util.clone(self, mutations = mutations)

  @classmethod
  def parse_str(clazz, s):
    xs, delim, ys = s.partition(',')
    x = int(xs.strip())
    y = int(ys.strip())
    return point(x, y)
  
  @classmethod
  def _check_cast_func(clazz, obj):
    return tuple_util.cast_seq_to_namedtuple(clazz, obj)
  
check.register_class(point, cast_func = point._check_cast_func)

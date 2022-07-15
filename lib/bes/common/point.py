#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.common.tuple_util import tuple_util

from ..system.check import check

class point(namedtuple('point', 'x, y')):

  def __new__(clazz, x = None, y = None):
    check.check_int(x, allow_none = True)
    check.check_int(y, allow_none = True)

    x = x or 0
    y = y or 0
    return clazz.__bases__[0].__new__(clazz, x, y)

  def __str__(self):
    return '{},{}'.format(self.x, self.y)

  def move(self, delta_x, delta_y):
    return point(self.x + delta_x, self.y + delta_y)

  def clone(self, mutations = None):
    return tuple_util.clone(self, mutations = mutations)

check.register_class(point)

#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from .check import check

class point(namedtuple('point', 'x,y')):

  def __new__(clazz, x = 0, y = 0):
    if not x or not y:
      x = 0
      y = 0
    return clazz.__bases__[0].__new__(clazz, x, y)

  def __str__(self):
    return '%d,%d' % (self.x, self.y)

  def move(self, x, y):
    return point(self.x + x, self.y + y)

check.register_class(point, 'point')

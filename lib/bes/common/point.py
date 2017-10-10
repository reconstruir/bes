#!/usr/bin/env python
#-*- coding:utf-8 -*-

from collections import namedtuple

class point(namedtuple('point', 'x,y')):

  def __new__(clazz, x = 0, y = 0):
    if not x or not y:
      x = 0
      y = 0
    return clazz.__bases__[0].__new__(clazz, x, y)

  def __str__(self):
    return '%d,%d' % (self.x, self.y)

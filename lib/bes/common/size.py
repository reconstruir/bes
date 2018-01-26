#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from .check import check

class size(namedtuple('size', 'width,height')):

  def __new__(clazz, width = 0, height = 0):
    width = width or 0
    height = height or 0
    if width == 0 or height == 0:
      width = 0
      height = 0
    check.check_int(width)
    check.check_int(height)
    return clazz.__bases__[0].__new__(clazz, width, height)

  def __str__(self):
    return '%dx%d' % (self.width, self.height)

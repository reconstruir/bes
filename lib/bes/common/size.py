#!/usr/bin/env python
#-*- coding:utf-8 -*-

from collections import namedtuple

class size(namedtuple('size', 'width,height')):

  def __new__(clazz, width = 0, height = 0):
    if not width or not height:
      width = 0
      height = 0
    return clazz.__bases__[0].__new__(clazz, width, height)

  def __str__(self):
    return '%dx%d' % (self.width, self.height)

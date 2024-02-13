#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from ..common.json_util import json_util
from ..common.tuple_util import tuple_util
from ..system.check import check

from .btl_document_position import btl_document_position

class btl_point(object):

  def __init__(self, x, y):
    self._pos = btl_document_position(y, x)

  @property
  def x(self):
    return self._pos.column

  @property
  def y(self):
    return self._pos.line

  def __iter__(self):
    yield self.x
    yield self.y

  def __str__(self):
    return f'{self.x},{self.y}'

  def to_dict(self):
    return { 'x': self.x, 'y': self.y }
  
  def move(self, delta_x, delta_y):
    return btl_point(self.x + delta_x, self.y + delta_y)

  def clone(self, mutations = None):
    if mutations and 'x' in mutations:
      x = mutations['x']
    else:
      x = self.x
    if mutations and 'y' in mutations:
      y = mutations['y']
    else:
      y = self.y
    return btl_point(x, y)

  @classmethod
  def parse_str(clazz, s):
    xs, delim, ys = s.partition(',')
    x = int(xs.strip())
    y = int(ys.strip())
    return btl_point(x, y)
  
  @classmethod
  def _check_cast_func(clazz, obj):
    if isinstance(obj, ( list, tuple )):
      return btl_point(*obj)
    assert False

  def advanced(self, c):
    self._pos = self._pos.advanced(c)
    
check.register_class(btl_point, cast_func = btl_point._check_cast_func)

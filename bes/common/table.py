#!/usr/bin/env python
#-*- coding:utf-8 -*-

#from string_lexer import string_lexer as lexer
#from StringIO import StringIO

from size import size

class table(object):
  'A 2 dimensional table table.'

  def __init__(self, size):
    self._size = size
    self._table = self._make_table(self._size)

  def resize(self, s):
    assert isinstance(s, size)
    if s == self._size:
      return

  def set(self, x, y, value):
    if not self.xy_valid(x, y):
      raise ValueError('Invalid coordinates: %s %s' % (str(x), str(y)))
    self._labels = labels
    
  def x_valid(self, x):
    return isinstance(x, int) and x >= 0 and x <= self.size.width
    
  def y_valid(self, y):
    return isinstance(y, int) and y >= 0 and y <= self.size.height
    
  def xy_valid(self, x, y):
    return self.x_valid(x) and self.y_valid(y)

  def _resize(self, size):
    if self._size == size:
      return
    new_table = self._make_table(size)
    self._size = size
    self._labels = None
    self._table = None

  @classmethod
  def _make_table(clazz, size):
    row = [ None ] * size.width
    rows = [ None ] * size.height
    for i in range(0, size.height):
      rows[i] = row
    return rows

  @classmethod
  def _clear_table(clazz, table):
    for y in range(0, len(table)):
      for x in range(0, len(table[y])):
        table[y][x] = None
        
  @classmethod
  def _copy_table(clazz, src, dst):
    clazz._clear_table(dst)
    for y in range(0, min(
    

#!/usr/bin/env python
#-*- coding:utf-8 -*-

#from string_lexer import string_lexer as lexer
#from StringIO import StringIO

from bes.common import object_util, size

class text_table(object):
  'Ascii table.'

  def __init__(self, size):
    self._size = size
    self._labels = None
    self._table = None

  def set_labels(self, labels):
    assert isinstance(labels, tuple)
    assert len(labels) == self._size.width
    self._labels = labels

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
    table = [ None ] * size.height
    for i in range(0, size.height):
      table[i] = row
    return table

  @classmethod
  def _clear_table(clazz, table):
    for y in range(0, len(table)):
      for x in range(0, len(table[y])):
        table[y][x] = None
        
  @classmethod
  def _copy_table(clazz, src, dst):
    clazz._clear_table(dst)
    for y in range(0, min(
    

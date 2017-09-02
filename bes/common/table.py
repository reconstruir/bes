#!/usr/bin/env python
#-*- coding:utf-8 -*-

from size import size

class table(object):
  'A 2 dimensional table table.'

  def __init__(self, width = 0, height = 0):
    assert width >= 0
    assert height >= 0
    self._size = size(width, height)
    self._table = self._make_table(self._size)

  @property
  def width(self):
    return self._size.width

  @property
  def height(self):
    return self._size.height

  @property
  def size(self):
    return self._size

  def resize(self, width, height):
    assert isinstance(width, int)
    assert isinstance(height, int)
    new_size = size(width, height)
    if new_size == self._size:
      return
    new_table = self._make_table(new_size)
    self._copy_table(self._table, new_table)
    self._table = new_table
    self._size = new_size

  def set(self, x, y, value):
    if not self.xy_valid(x, y):
      raise ValueError('Invalid cell: (%s, %s)' % (str(x), str(y)))
    self._table[y][x] = value

  def set_row(self, y, row):
    if not isinstance(row, tuple):
      raise TypeError('row needs to be a tuple instead of: %s' % (type(row)))
    if not self.y_valid(y):
      raise ValueError('Invalid y: %s' % (str(y)))
    if len(row) != self._width:
      raise ValueError('Row should be %d wide instead of: ' % (self._width, len(row)))
    for x in range(0, self._width):
      self._table[y][x] = row[x]
    
  def set_column(self, x, column):
    if not isinstance(column, tuple):
      raise TypeError('column needs to be a tuple instead of: %s' % (type(column)))
    if not self.x_valid(x):
      raise ValueError('Invalid x: %s' % (str(x)))
    if len(column) != self._height:
      raise ValueError('Column should be %d high instead of: ' % (self._height, len(column)))
    for y in range(0, self._height):
      self._table[y][x] = column[y]
    
  def get(self, x, y):
    if not self.xy_valid(x, y):
      raise ValueError('Invalid cell: (%s, %s)' % (str(x), str(y)))
    return self._table[y][x]

  def row(self, y):
    if not self.y_valid(y):
      raise ValueError('Invalid y: %s' % (str(y)))
    return self._table[y]
  
  def column(self, x):
    if not self.x_valid(y):
      raise ValueError('Invalid x: %s' % (str(x)))
    col = []
    for y in range(0, self._height):
      col.append(self._table[y][x])
    return col
  
  def x_valid(self, x):
    return isinstance(x, int) and x >= 0 and x < self.size.width
    
  def y_valid(self, y):
    return isinstance(y, int) and y >= 0 and y < self.size.height
    
  def xy_valid(self, x, y):
    return self.x_valid(x) and self.y_valid(y)

  @classmethod
  def _make_table(clazz, size):
    rows = [ None ] * size.height
    for i in range(0, size.height):
      rows[i] = [ None ] * size.width
    return rows

  @classmethod
  def _clear_table(clazz, table):
    for y in range(0, len(table)):
      for x in range(0, len(table[y])):
        table[y][x] = None
        
  @classmethod
  def _copy_table(clazz, src, dst):
    clazz._clear_table(dst)
    for y in range(0, min(len(src), len(dst))):
      for x in range(0, min(len(src[y]), len(dst[y]))):
        dst[y][x] = src[y][x]

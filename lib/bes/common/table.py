#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .check import check
from .size import size
from .string_util import string_util
from bes.compat import StringIO

class table(object):
  'A 2 dimensional table.'

  def __init__(self, width = None, height = None, data = None, default_value = None):
    self._default_value = default_value
    if data is not None and width is not None and width != len(data[0]):
      raise ValueError('width should be %d instead of %d' % (len(data[0]), width))
      
    if data is not None and height is not None and height != len(data):
      raise ValueError('height should be %d instead of %d' % (len(data), height))

    if data is not None:
      if isinstance(data, table):
        width = data.width
        height = data.height
      else:
        if len(data) > 0:
          width = len(data[0])
          height = len(data)
        else:
          width = 0
          height = 0

    if width is None or height is None:
      width = 0
      height = 0
      
    check.check_int(width)
    check.check_int(height)
    self._size = size(width, height)
    self._table = self._make_table(self._size, self._default_value)
    if data:
      self.set_data(data)
    
  @property
  def width(self):
    return self._size.width

  @property
  def height(self):
    return self._size.height

  @property
  def size(self):
    return self._size

  def __str__(self):
    max_len = 0
    for y in range(0, self.height):
      for x in range(0, self.width):
        max_len = max(len(str(self._table[y][x])), max_len)
    buf = StringIO()
    for y in range(0, self.height):
      for x in range(0, self.width):
        buf.write(string_util.right_justify(str(self._table[y][x]), max_len))
        buf.write(' ')
      buf.write('\n')
    return buf.getvalue()

  def __repr__(self):
    return str(self)
  
  def __eq__(self, other):
    if self.size != other.size:
      return False
    for y in range(0, self.height):
      for x in range(0, self.width):
        if self._table[y][x] != other._table[y][x]:
          return False
    return True
    
  def resize(self, width, height):
    check.check_int(width)
    check.check_int(height)
    new_size = size(width, height)
    if new_size == self._size:
      return
    new_table = self._make_table(new_size, self._default_value)
    self._copy_table(self._table, new_table, self._default_value)
    self._table = new_table
    self._size = new_size

  def set(self, x, y, value):
    self.check_xy(x, y)
    self._table[y][x] = value

  def get(self, x, y):
    self.check_xy(x, y)
    return self._table[y][x]
    
  def set_row(self, y, row):
    check.check_tuple(row)
    self.check_y(y)
    if len(row) != self._size.width:
      raise ValueError('Row should be %d wide instead of %d: \"%s\"' % (self._size.width, len(row), str(row)))
    for x in range(0, self._size.width):
      self._table[y][x] = row[x]
    
  def set_column(self, x, column):
    check.check_tuple(column)
    self.check_x(x)
    if len(column) != self._size.height:
      raise ValueError('Column should be %d high instead of %d: \"%s\"' % (self._size.height, len(column), str(column)))
    for y in range(0, self._size.height):
      self._table[y][x] = column[y]
   
  def sort_by_column(self, x, key = None):
    self.check_x(x)
    self._table = sorted(self._table, key = key or (lambda row: row[x]))

  def row(self, y):
    self.check_y(y)
    return tuple(self._table[y])
  
  def column(self, x):
    self.check_x(x)
    col = []
    for y in range(0, self._size.height):
      col.append(self._table[y][x])
    return tuple(col)
  
  def x_valid(self, x):
    return check.is_int(x) and x >= 0 and x < self.size.width
    
  def y_valid(self, y):
    return check.is_int(y) and y >= 0 and y < self.size.height
    
  def xy_valid(self, x, y):
    return self.x_valid(x) and self.y_valid(y)

  def width_valid(self, width):
    return check.is_int(width) and width == self.size.width

  def height_valid(self, height):
    return check.is_int(height) and height == self.size.height

  def check_x(self, x):
    if not self.x_valid(x):
      raise ValueError('Invalid x: %s' % (str(x)))

  def check_y(self, y):
    if not self.y_valid(y):
      raise ValueError('Invalid y: %s' % (str(y)))

  def check_xy(self, x, y):
    if not self.xy_valid(x, y):
      raise ValueError('Invalid x, y: %s, %s' % (str(x), str(y)))

  def check_width(self, width):
    if not self.width_valid(width):
      raise ValueError('Invalid width: %s' % (str(width)))

  def check_height(self, height):
    if not self.height_valid(height):
      raise ValueError('Invalid height: %s' % (str(height)))

  @classmethod
  def _make_table(clazz, size, default_value):
    rows = [ default_value ] * size.height
    for i in range(0, size.height):
      rows[i] = [ default_value ] * size.width
    return rows

  @classmethod
  def _clear_table(clazz, table, default_value):
    for y in range(0, len(table)):
      for x in range(0, len(table[y])):
        table[y][x] = default_value
        
  @classmethod
  def _copy_table(clazz, src, dst, default_value):
    clazz._clear_table(dst, default_value)
    for y in range(0, min(len(src), len(dst))):
      for x in range(0, min(len(src[y]), len(dst[y]))):
        dst[y][x] = src[y][x]

  def set_data(self, data):
    if isinstance(data, table):
      self._table = data._table
    else:
      check.check_tuple_seq(data)
      if len(data) != self.height:
        raise ValueError('Length of data should be %d instead of %d' % (self.height, len(data)))
      for i, row in enumerate(data):
        self.set_row(i, row)

  def insert_column(self, col_x, column = None):
    self.check_x(col_x)
    new_table = table(self.width + 1, self.height, default_value = self._default_value)
    for x in range(0, col_x):
      new_table.set_column(x, self.column(x))
    new_col_x = col_x + 1
    for x in range(col_x, self.width):
      new_table.set_column(new_col_x, self.column(x))
      new_col_x = new_col_x + 1
    self._size = new_table._size
    self._table = new_table._table
    if column:
      self.set_column(col_x, column)

  def insert_row(self, row_y, row = None):
    self.check_y(row_y)
    new_row = [ self._default_value ] * self._size.width
    self._table.insert(row_y, new_row)
    self._size = size(self.width, self.height + 1)
    if row:
      self.set_row(row_y, row)
      

#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .check import check
from .size import size
from .string_util import string_util
from bes.compat import StringIO

class table_row(list):

  def __init__(self, *args, **kwargs):
    list.__init__(self, *args, **kwargs)
    self._column_names = None
    
  def __getattr__(self, key):
    if not self._column_names:
      raise ValueError('column names are empty.')
    try:
      return self[self._column_names.index(key)]
    except ValueError as ex:
      raise ValueError('unknown field: \"%s\"' % (key))
  
class table(object):
  'A 2 dimensional table.'

  def __init__(self, width = None, height = None, data = None, default_value = None, column_names = None):
    self._default_value = default_value

    if column_names:
      check.check_tuple(column_names)
      
    self._column_names = column_names
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
    self._rows = self._make_table(width, height, self._default_value)
    if data:
      self.set_data(data)

  def __getitem__(self, y):
    self.check_y(y)
    return self._rows[y]

  @property
  def empty(self):
    return self.width == 0 or self.height == 0
  
  @property
  def width(self):
    if not self._rows:
      return 0
    return len(self._rows[0])

  @property
  def height(self):
    if not self._rows:
      return 0
    return len(self._rows)

  def __iter__(self):
    'Iterate through the table rows'
    return iter(self._rows)
  
  def __str__(self):
    max_len = 0
    for y in range(0, self.height):
      for x in range(0, self.width):
        max_len = max(len(str(self._rows[y][x])), max_len)
    buf = StringIO()
    for y in range(0, self.height):
      for x in range(0, self.width):
        buf.write(string_util.right_justify(str(self._rows[y][x]), max_len))
        buf.write(' ')
      buf.write('\n')
    return buf.getvalue()

  def __repr__(self):
    return str(self)
  
  def __eq__(self, other):
    if self.width != other.width or self.height != other.height:
      return False
    for y in range(0, self.height):
      for x in range(0, self.width):
        if self._rows[y][x] != other._rows[y][x]:
          return False
    return True
    
  def resize(self, width, height):
    check.check_int(width)
    check.check_int(height)
    if width == self.width and height == self.height:
      return
    new_table = self._make_table(width, height, self._default_value)
    self._copy_table(self._rows, new_table, self._default_value)
    self._rows = new_table

  def set(self, x, y, value):
    self.check_xy(x, y)
    self._rows[y][x] = value

  def get(self, x, y):
    self.check_xy(x, y)
    return self._rows[y][x]
    
  def set_row(self, y, row):
    check.check(row, ( tuple, list ))
    self.check_y(y)
    if len(row) != self.width:
      raise ValueError('Row should be %d wide instead of %d: \"%s\"' % (self.width, len(row), str(row)))
    for x in range(0, self.width):
      self._rows[y][x] = row[x]
    
  def set_column(self, x, column):
    check.check_tuple(column)
    self.check_x(x)
    if len(column) != self.height:
      raise ValueError('Column should be %d high instead of %d: \"%s\"' % (self.height, len(column), str(column)))
    for y in range(0, self.height):
      self._rows[y][x] = column[y]
   
  def sort_by_column(self, x, reverse = False):
    self.check_x(x)
    self.sort_by_key((lambda row: row[x]), reverse = reverse)

  def sort_by_key(self, key, reverse = False):
    self._rows = sorted(self._rows, key = key, reverse = reverse)

  def row(self, y):
    self.check_y(y)
    return tuple(self._rows[y])
  
  def column(self, x):
    self.check_x(x)
    col = []
    for y in range(0, self.height):
      col.append(self._rows[y][x])
    return tuple(col)
  
  def x_valid(self, x):
    return check.is_int(x) and x >= 0 and x < self.width
    
  def y_valid(self, y):
    return check.is_int(y) and y >= 0 and y < self.height
    
  def xy_valid(self, x, y):
    return self.x_valid(x) and self.y_valid(y)

  def width_valid(self, width):
    return check.is_int(width) and width == self.width

  def height_valid(self, height):
    return check.is_int(height) and height == self.height

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

  def _make_table(self, width, height, default_value):
    rows = [ default_value ] * height
    for i in range(0, height):
      rows[i] = table_row([ default_value ] * width)
      rows[i]._column_names = self._column_names
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
      self._rows = data._rows
    else:
      check.check_tuple_seq(data)
      if len(data) != self.height:
        raise ValueError('Length of data should be %d instead of %d' % (self.height, len(data)))
      for i, row in enumerate(data):
        self.set_row(i, row)

  def insert_column(self, col_x, column = None, name = None):
    if self.empty:
      if not column:
        raise ValueError('first column cannot be None.')
      if col_x != 0:
        raise ValueError('first column should be 0 instead of %d' % (col_x))
      self._insert_column_empty(column, name = name)
    else:
      self.check_x(col_x)
      self._insert_column_not_empty(col_x, column = column, name = name)

  def _insert_column_empty(self, column, name = None):
    if name:
      check.check_string(name)
      new_column_names = [ name ]
    else:
      new_column_names = None
    new_table = table(1, len(column), default_value = self._default_value, column_names = new_column_names)
    self._rows = new_table._rows
    self.set_column(0, column)

  def _insert_column_not_empty(self, col_x, column = None, name = None):
    new_table = table(self.width + 1, self.height, default_value = self._default_value, column_names = self._column_names)
    for x in range(0, col_x):
      new_table.set_column(x, self.column(x))
    new_col_x = col_x + 1
    for x in range(col_x, self.width):
      new_table.set_column(new_col_x, self.column(x))
      new_col_x = new_col_x + 1
    self._rows = new_table._rows
    if column:
      self.set_column(col_x, column)

    
  def remove_column(self, col_x):
    self.check_x(col_x)
    new_table = table(self.width - 1, self.height, default_value = self._default_value, column_names = self._column_names)
    for x in range(0, col_x):
      new_table.set_column(x, self.column(x))
    new_x = col_x + 1
    for old_x in range(col_x, self.width):
      new_table.set_column(new_x, self.column(old_x))
      new_x = new_x + 1
    self._rows = new_table._rows
    if column:
      self.set_column(col_x, column)

  def remove_column(self, col_x):
    self.check_x(col_x)
    new_column_names = self._remove_column_name(self._column_names, col_x)
    new_table = table(self.width - 1, self.height, default_value = self._default_value, column_names = new_column_names)
    for x in range(0, col_x):
      new_table.set_column(x, self.column(x))
    new_x = col_x
    for old_x in range(col_x + 1, self.width):
      new_table.set_column(new_x, self.column(old_x))
      new_x = new_x + 1
    self._rows = new_table._rows
    self._column_names = new_column_names

  def _remove_column_name(clazz, column_names, x):
    if not column_names:
      return None
    assert x >= 0 and x < len(column_names)
    l = list(column_names)
    l.pop(x)
    return tuple(l)
      
  def insert_row(self, row_y, row = None):
    if self._rows == []:
      if row is None:
        raise ValueError('The first row cannot be None')
      check.check(row, ( list, tuple ))
      new_row = table_row([ item for item in row ])
      new_row._column_names = self._column_names
      self._rows = [ new_row ]
    else:
      self.check_y(row_y)
      new_row = table_row([ self._default_value ] * self.width)
      new_row._column_names = self._column_names
      self._rows.insert(row_y, new_row)
      if row:
        self.set_row(row_y, row)
      
  def append_row(self, row = None):
    return self.insert_row(0, row = row)
      
  def append_rows(self, rows):
    if check.is_table(rows):
      rows = rows._rows
    check.check_list(rows)
    rows_width = len(rows[0])
    if len(rows[0]) != self.width:
      raise ValueError('rows width should be %d instead of %d' % (self.width, rows_width))
    for row in rows:
      new_row = table_row(row)
      new_row._column_names = self._column_names
      self._rows.append(new_row)

  @classmethod
  def concatenate_vertical(clazz, tables):
    'Concatenate a sequence of tables vertically.  The column width for all tables must match the first table.'
    check.check_table_seq(tables)
    tables = [ t for t in tables if not t.empty ]
    result = None
    for i, t in enumerate(tables):
      if not result:
        result = t
      else:
        if t.width != result.width:
          raise ValueError('table %d - width should be %d instead of %d' % (result.width, t.width))
        result.append_rows(t)
    return result or table()

  def filter_rows(self, filter_func):
    'Filter rows with filter_func.'
    assert callable(filter_func)
    new_table = table(column_names = self._column_names)
    for row in self._rows:
      if filter_func(row):
        new_table.append_row(row)
    return new_table
  
check.register_class(table)

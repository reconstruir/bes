#!/usr/bin/env python
#-*- coding:utf-8 -*-

from bes.common import object_util, table, size
from StringIO import StringIO

class text_table_cell_style(object):

  JUST_LEFT = 'left'
  JUST_RIGHT = 'right'

  def __init__(self, just = None, width = None):
    self.just = just or self.JUST_LEFT
    self.width = width or 0

  def format(self, value, width = None):
    width = width or self.width or 0
    if self.just == self.JUST_LEFT:
      value = value.ljust(width)
    elif self.just == self.JUST_RIGHT:
      value = value.rjust(width)
    else:
      raise ValueError('Invalid just: %s' % (self.just))
      
    return value

class text_table(object):
  'A table of strings.'
  def __init__(self, width, height, column_delimiter = ' │ '):
    self._labels = None
    self._table = table(width, height)
    self._column_delimiter = column_delimiter
    self._row_styles = {}
    self._col_styles = {}
    self._cell_styles = {}
    self._default_cell_style = text_table_cell_style()
    
  def set_labels(self, labels):
    self._table.check_width(len(labels))
    assert isinstance(labels, tuple)
    self._labels = labels[:]

  def set(self, x, y, s):
    if not isinstance(s, ( str, unicode )):
      raise ValueError('s should be a string instead of: %s' % (type(s)))
    self._table.set(x, y, s)
    
  def get(self, x, y):
    return self._table.get(x, y)

  def __str__(self):
    buf = StringIO()
    col_widths = [ self._column_width(x) for x in range(0, self._table.width) ]
    if self._labels:
      for x in range(0, self._table.width):
        self._write_label(x, buf, col_widths)
      buf.write('\n')
    for y in range(0, self._table.height):
      row = self._table.row(y)
      assert len(row) == len(col_widths)
      for x in range(0, self._table.width):
        self._write_cell(x, y, buf, col_widths)
      buf.write('\n')
    value = buf.getvalue()
    # remove the trailing new line
    return value[0:-1]

  def _write_cell(self, x, y, stream, col_widths):
    value = str(self._table.get(x, y)) or ''
    style = self.get_cell_style(x, y)
    assert style
    value = style.format(value, width = col_widths[x])
    stream.write(value)
    stream.write(self._column_delimiter)
  
  def _write_label(self, x, stream, col_widths):
    value = str(self._labels[x])
    style = self.get_cell_style(x, 0)
    assert style
    value = style.format(value, width = col_widths[x])
    stream.write(value)
    stream.write(self._column_delimiter)
  
  def _column_width(self, x):
    self._table.check_x(x)
    max_col_width = max([len(str(s)) for s in self._table.column(x)])
    if self._labels:
      max_col_width = max(max_col_width, len(self._labels[x]))
    return max_col_width
  
  def sort_by_column(self, x):
    self._table.check_x(x)
    self._table.sort_by_column(x)

  def set_row(self, y, row):
    self._table.check_y(y)
    self._table.set_row(y, row)

  def set_row_style(self, y, style):
    self._table.check_y(y)
    self._row_styles[y] = style

  def set_col_style(self, x, style):
    self._table.check_x(x)
    self._col_styles[x] = style
    
  def set_cell_style(self, x, y, style):
    self._table.check_xy(x, y)
    self._cell_styles[(x, y)] = style
    
  def get_cell_style(self, x, y):
    self._table.check_xy(x, y)
    return self._cell_styles.get((x, y), None) or self._col_styles.get(x, self._default_cell_style)

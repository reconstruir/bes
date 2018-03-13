#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import check, object_util, table, size
from bes.compat import StringIO

class text_cell_renderer(object):

  JUST_LEFT = 'left'
  JUST_RIGHT = 'right'

  def __init__(self, just = None, width = None):
    self.just = just or self.JUST_LEFT
    self.width = width or 0

  def render(self, value, width = None):
    if value:
      vs = str(value)
    else:
      vs = ''
    width = width or self.width or 0
    if self.just == self.JUST_LEFT:
      vs = vs.ljust(width)
    elif self.just == self.JUST_RIGHT:
      vs = vs.rjust(width)
    else:
      raise ValueError('Invalid just: %s' % (self.just))
    return vs

  def compute_width(self, value):
    return len(self.render(value, width = None))
  
class text_table(object):
  'A table of strings.'
  def __init__(self, width = None, height = None, data = None, column_delimiter = ' │ '):
    self._labels = None
    self._table = table(width = width, height = height, data = data)
    self._column_delimiter = column_delimiter
    self._row_renderers = {}
    self._col_renderers = {}
    self._cell_renderers = {}
    self._default_cell_renderer = text_cell_renderer()
    
  def set_labels(self, labels):
    check.check_tuple(labels)
    self._table.check_width(len(labels))
    self._labels = labels[:]

  def set(self, x, y, s):
    check.check_string(s)
    self._table.set(x, y, s)
    
  def get(self, x, y):
    return self._table.get(x, y)

  def __str__(self):
    return self.to_string()

  def to_string(self, strip_rows = True):
    buf = StringIO()
    col_widths = self.column_widths()
    if self._labels:
      for x in range(0, self._table.width):
        self._write_label(x, buf, col_widths)
      buf.write('\n')
    for y in range(0, self._table.height):
      row = self._table.row(y)
      assert len(row) == len(col_widths)
      row_buf = StringIO()
      for x in range(0, self._table.width):
        self._write_cell(x, y, row_buf, col_widths)
      row_str = row_buf.getvalue()
      if strip_rows:
        row_str = row_str.strip()
      buf.write(row_str)
      buf.write('\n')
    value = buf.getvalue()
    # remove the trailing new line
    return value[0:-1]

  def _write_cell(self, x, y, stream, col_widths):
    value = self._table.get(x, y)
    renderer = self.get_cell_renderer(x, y)
    assert renderer
    value_string = renderer.render(value, width = col_widths[x])
    stream.write(value_string)
    stream.write(self._column_delimiter)
  
  def _write_label(self, x, stream, col_widths):
    value = self._labels[x]
    renderer = self.get_cell_renderer(x, 0)
    assert renderer
    value = renderer.render(value, width = col_widths[x])
    stream.write(value)
    stream.write(self._column_delimiter)
  
  def _column_width(self, x):
    self._table.check_x(x)
    max_col_width = self._max_column_width(x)
    if self._labels:
      max_col_width = max(max_col_width, len(self._labels[x]))
    return max_col_width
  
  def _max_column_width(self, x):
    self._table.check_x(x)
    max_width = 0
    for y in range(0, self._table.height):
      renderer = self.get_cell_renderer(x, y)
      value = self._table.get(x, y)
      max_width = max(max_width, renderer.compute_width(value))
    return max_width
  
  def sort_by_column(self, x):
    self._table.check_x(x)
    self._table.sort_by_column(x)

  def set_row(self, y, row):
    self._table.check_y(y)
    self._table.set_row(y, row)

  def set_row_renderer(self, y, renderer):
    self._table.check_y(y)
    self._row_renderers[y] = renderer

  def set_col_renderer(self, x, renderer):
    self._table.check_x(x)
    self._col_renderers[x] = renderer
    
  def set_cell_renderer(self, x, y, renderer):
    self._table.check_xy(x, y)
    self._cell_renderers[(x, y)] = renderer
    
  def get_cell_renderer(self, x, y):
    self._table.check_xy(x, y)
    return self._cell_renderers.get((x, y), None) or self._col_renderers.get(x, self._default_cell_renderer)

  def set_data(self, data):
    check.check_tuple_seq(data)
    self._table.set_data(data)

  def column_widths(self):
    return tuple([ self._column_width(x) for x in range(0, self._table.width) ])

  @property
  def default_cell_renderer(self):
    return self._default_cell_renderer
  
  @default_cell_renderer.setter
  def default_cell_renderer(self, renderer):
    if renderer:
      assert isinstance(renderer, text_cell_renderer)
    else:
      renderer = text_cell_renderer()
    self._default_cell_renderer = renderer
    print('default renderer changed from %s to %s' % (self._default_cell_renderer, renderer))

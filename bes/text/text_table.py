#!/usr/bin/env python
#-*- coding:utf-8 -*-

from bes.common import object_util, table, size
from cStringIO import StringIO

class text_table(object):
  'A table of strings.'

  def __init__(self, width, height):
    self._labels = None
    self._table = table(width, height)

  def set_labels(self, labels):
    assert isinstance(labels, tuple)
    assert len(labels) == self.table.width
    self._labels = labels

  def set(self, x, y, s):
    if not isinstance(s, ( str, unicode )):
      raise ValueError('s should be a string instead of: %s' % (type(s)))
    self._table.set(x, y, s)
    
  def get(self, x, y):
    return self._table.get(x, y)

  def __str__(self):
    buf = StringIO()
    column_widths = [ self._column_width(x) for x in range(0, self._table.width) ]
    for y in range(0, self._table.height):
      row = self._table.row(y)
      assert len(row) == len(column_widths)
      for x in range(0, self._table.width):
        value = str(self._table.get(x, y)) or ''
        buf.write(value.ljust(column_widths[x]))
        buf.write(' ')
      buf.write('\n')
    buf.write('\n')
    return buf.getvalue()

  def _column_width(self, x):
    return max([len(str(s)) for s in self._table.column(x)])
  
  def sort_by_column(self, x):
    self._table.sort_by_column(x)

  def set_row(self, y, row):
    self._table.set_row(y, row)


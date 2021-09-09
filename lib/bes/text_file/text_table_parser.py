#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check
from bes.common.table import table
from bes.compat.StringIO import StringIO
from .text_line_parser import text_line_parser

class text_table_parser(object):
  'Parse text into a table.'

  def __init__(self, text, column_widths):
    check.check_string(text)
    check.check_tuple(column_widths)
    self.table = self._parse(text, column_widths)

  def __str__(self):
    return str(self.table)
    
  def __repr__(self):
    return str(self)
    
  @classmethod
  def _parse(clazz, text, column_widths):
    lines = text_line_parser(text)
    data = []
    for line in lines:
      ltext = line.text
      if ltext:
        row = clazz._line_to_columns(ltext, column_widths)
        data.append(tuple(row))
    return table(data = data)

  @classmethod
  def _line_to_columns(clazz, ltext, column_widths):
    cols = []
    buf = StringIO(ltext)
    for col_width in column_widths:
      cols.append(clazz._buf_to_str(buf, col_width))
    return cols
  
  @classmethod
  def _buf_to_str(clazz, buf, col_width):
    col_buf = StringIO()
    for i in range(0, col_width):
      c = buf.read(1)
      if c:
        col_buf.write(c)
      else:
        break
    return col_buf.getvalue().strip() or None

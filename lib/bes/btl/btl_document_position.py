#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from ..common.tuple_util import tuple_util
from ..system.check import check
    
class btl_document_position(namedtuple('btl_document_position', 'line, column')):

  def __new__(clazz, line, column):
    check.check_int(line)
    check.check_int(column)
    
    return clazz.__bases__[0].__new__(clazz, line, column)

  def __str__(self):
    return f'{self.line},{self.column}'

  def to_dict(self):
    return dict(self._asdict())
  
  def moved(self, delta_line, delta_column):
    return btl_document_position(self.line + delta_line,
                                 self.column + delta_column)

  def clone(self, mutations = None):
    return tuple_util.clone(self, mutations = mutations)

  @classmethod
  def parse_str(clazz, s):
    check.check_string(s)

    line_str, delim, column_str = s.partition(',')
    if delim.strip() != ',':
      raise ValueError(f'Invalid position: "{s}"')
    line = int(line_str.strip())
    column = int(column_str.strip())
    return btl_document_position(line, column)
  
  @classmethod
  def _check_cast_func(clazz, obj):
    return tuple_util.cast_seq_to_namedtuple(clazz, obj)

  def advanced(self, c):
    if c in ( '\n', '\r\n' ):
      line = self.line + 1
      column = 0
    else:
      line = self.line
      column = self.column + len(c)
    return btl_document_position(line, column)

  def moved_horizontal(self, delta_column):
    check.check_int(delta_column)

    return self.moved(0, delta_column)

  def moved_vertical(self, delta_line):
    check.check_int(delta_line)

    return self.moved(delta_line, 0)

  def moved_to_line(self, line):
    check.check_int(line)

    return btl_document_position(line, self.column)
  
check.register_class(btl_document_position, cast_func = btl_document_position._check_cast_func)

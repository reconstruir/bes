#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from ..common.json_util import json_util
from ..common.tuple_util import tuple_util
from ..system.check import check

class btl_document_position(namedtuple('btl_document_position', 'line_number, column')):

  def __new__(clazz, line_number, column):
    check.check_int(line_number)
    check.check_int(column)
    
    return clazz.__bases__[0].__new__(clazz, line_number, column)

  def __str__(self):
    return f'{self.line_number},{self.column}'

  def to_dict(self):
    return dict(self._asdict())
  
  def moved(self, delta_line_number, delta_column):
    return btl_document_position(self.line_number + delta_line_number,
                                 self.column + delta_column)

  def clone(self, mutations = None):
    return tuple_util.clone(self, mutations = mutations)

  @classmethod
  def parse_str(clazz, s):
    check.check_string(s)

    xs, delim, ys = s.partition(',')
    x = int(xs.strip())
    y = int(ys.strip())
    return btl_document_position(x, y)
  
  @classmethod
  def _check_cast_func(clazz, obj):
    return tuple_util.cast_seq_to_namedtuple(clazz, obj)
  
check.register_class(btl_document_position, cast_func = btl_document_position._check_cast_func)

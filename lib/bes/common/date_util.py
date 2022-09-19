#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from datetime import datetime

from ..system.check import check
from ..enum_util.checked_enum import checked_enum

class date_util(object):
  'Date util'

  class date_util_compare_operator(checked_enum):
    EQ = 'eq'
    GE = 'ge'
    GT = 'gt'
    LE = 'le'
    LT = 'lt'
    NE = 'ne'
  date_util_compare_operator.register_check_class()
  
  @classmethod
  def compare(clazz, d1, d2, operator):
    'Compare 2 datetime objects with operator'
    check.check_datetime(d1)
    check.check_datetime(d2)
    operator = check.check_date_util_compare_operator(operator)

    if operator == clazz.date_util_compare_operator.EQ:
      result = d1 == d2
    elif operator == clazz.date_util_compare_operator.NE:
      result = d1 != d2
    elif operator == clazz.date_util_compare_operator.LT:
      result = d1 < d2
    elif operator == clazz.date_util_compare_operator.LE:
      result = d1 <= d2
    elif operator == clazz.date_util_compare_operator.GT:
      result = d1 > d2
    elif operator == clazz.date_util_compare_operator.GE:
      result = d1 >= d2
    else:
      assert False, 'not reached'
    return result

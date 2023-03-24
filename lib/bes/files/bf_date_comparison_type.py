#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.enum_util.checked_enum import checked_enum

class bf_date_comparison_type(checked_enum):
  EQ = 'eq'
  GE = 'ge'
  GT = 'gt'
  LE = 'le'
  LT = 'lt'
  NE = 'ne'
  
bf_date_comparison_type.register_check_class()

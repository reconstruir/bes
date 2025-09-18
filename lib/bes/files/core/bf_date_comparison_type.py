#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_type_checked_enum import bcli_type_checked_enum
from bes.enum_util.checked_enum import checked_enum

class bf_date_comparison_type(checked_enum):
  EQ = 'eq'
  GE = 'ge'
  GT = 'gt'
  LE = 'le'
  LT = 'lt'
  NE = 'ne'
  
bf_date_comparison_type.register_check_class()

class bf_date_comparison_type_cli(bcli_type_checked_enum):
  __enum_class__ = bf_date_comparison_type

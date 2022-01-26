#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.enum_util.checked_enum import checked_enum

class dir_split_conflict_strategy(checked_enum):
  ERROR = 'error'
  RENAME = 'rename'
  REPLACE = 'replace'

dir_split_conflict_strategy.register_check_class()

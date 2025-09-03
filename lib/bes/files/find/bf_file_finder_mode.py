#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_type_checked_enum import bcli_type_checked_enum
from bes.enum_util.checked_enum import checked_enum

class bf_file_finder_mode(checked_enum):
  IMMEDIATE     = 'immediate'
  WITH_PROGRESS = 'with_progress'
  
bf_file_finder_mode.register_check_class()

class bf_cli_file_finder_mode(bcli_type_checked_enum):
  __enum_class__ = bf_file_finder_mode

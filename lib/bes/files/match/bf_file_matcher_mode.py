#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_type_checked_enum import bcli_type_checked_enum
from bes.enum_util.checked_enum import checked_enum

class bf_file_matcher_mode(checked_enum):
  ALL = 'all'
  ANY = 'any'
  NONE = 'none'
  
bf_file_matcher_mode.register_check_class()

class bf_cli_file_matcher_type(bcli_type_checked_enum):
  __enum_class__ = bf_file_matcher_mode

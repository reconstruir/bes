#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_type_checked_enum import bcli_type_checked_enum
from bes.enum_util.checked_enum import checked_enum

class pyinstaller_log_level(checked_enum):
  CRITICAL = 'critical'
  DEBUG = 'debug'
  ERROR = 'error'
  INFO = 'info'
  TRACE = 'trace'
  WARN = 'warn'

pyinstaller_log_level.register_check_class()

class cli_pyinstaller_log_level_type(bcli_type_checked_enum):
  __enum_class__ = pyinstaller_log_level

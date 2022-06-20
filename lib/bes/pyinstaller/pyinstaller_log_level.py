#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.enum_util.checked_enum import checked_enum

class pyinstaller_log_level(checked_enum):
  CRITICAL = 'critical'
  DEBUG = 'debug'
  ERROR = 'error'
  INFO = 'info'
  TRACE = 'trace'
  WARN = 'warn'
  
pyinstaller_log_level.register_check_class()

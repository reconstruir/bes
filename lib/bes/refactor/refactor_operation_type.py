#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.enum_util.checked_enum import checked_enum

class refactor_operation_type(checked_enum):
  COPY_FILES = 'copy_files'
  RENAME_FILES = 'rename_files'
  RENAME_DIRS = 'rename_dirs'

refactor_operation_type.register_check_class()
  

#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

#from bes.bcli.bcli_type_checked_enum import bcli_type_checked_enum
from bes.enum_util.checked_enum import checked_enum

class bf_entry_sort_type(checked_enum):
  BASENAME = 'basename'
  BASENAME_LOWERCASE = 'basename_lowercase'
  DIRNAME = 'dirname'
  DIRNAME_LOWERCASE = 'dirname_lowercase'
  FILENAME = 'filename'
  FILENAME_LOWERCASE = 'filename_lowercase'
  MODIFICATION_DATE = 'modification_date'
  SIZE = 'size'
  
bf_entry_sort_type.register_check_class()

#class bf_cli_path_type(bcli_type_checked_enum):
#  __enum_class__ = bf_entry_sort_type

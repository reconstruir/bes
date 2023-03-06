#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.enum_util.checked_enum import checked_enum

class bfile_filename_match_type(checked_enum):
  ALL = 'ALL'
  ANY = 'ANY'
  NONE = 'NONE'
  
bfile_filename_match_type.register_check_class()

#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.enum_util.checked_enum import checked_enum

class bfile_matcher_path_type(checked_enum):
  ABSOLUTE = 'absolute'
  BASENAME = 'basename'
  RELATIVE = 'relative'
  
bfile_matcher_path_type.register_check_class()

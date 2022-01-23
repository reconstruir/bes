#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.enum_util.checked_enum import checked_enum

class file_poto_type(checked_enum):
  PREFIX = 'prefix'
  MEDIA_TYPE = 'media_type'

file_poto_type.register_check_class()

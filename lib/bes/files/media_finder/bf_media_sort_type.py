#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.enum_util.checked_enum import checked_enum

class bf_media_sort_type(checked_enum):
  FOUND_ORDER = 'found_order'
  NAME        = 'name'
  PATH        = 'path'
  DATE        = 'date'
  SIZE        = 'size'
  KIND        = 'kind'

bf_media_sort_type.register_check_class()

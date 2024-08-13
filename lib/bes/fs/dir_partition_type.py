#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_type_checked_enum import bcli_type_checked_enum
from bes.enum_util.checked_enum import checked_enum

class dir_partition_type(checked_enum):
  CRITERIA = 'criteria'
  MEDIA_TYPE = 'media_type'
  PREFIX = 'prefix'

dir_partition_type.register_check_class()

class cli_dir_partition_type(bcli_type_checked_enum):
  __enum_class__ = dir_partition_type

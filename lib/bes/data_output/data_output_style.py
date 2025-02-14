#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_type_checked_enum import bcli_type_checked_enum
from bes.enum_util.checked_enum import checked_enum

class data_output_style(checked_enum):
  BRIEF = 'brief'
  CSV = 'csv'
  JSON = 'json'
  PLAIN_TABLE = 'plain_table'
  RAW = 'raw'
  RAW_PRETTY = 'raw_pretty'
  TABLE = 'table'

data_output_style.register_check_class()

class data_output_style_cli(bcli_type_checked_enum):
  __enum_class__ = data_output_style

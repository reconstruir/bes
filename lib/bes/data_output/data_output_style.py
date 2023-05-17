#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.enum_util.checked_enum import checked_enum

class data_output_style(checked_enum):
  BRIEF = 'brief'
  CSV = 'csv'
  JSON = 'json'
  PLAIN_TABLE = 'plain_table'
  RAW = 'raw'
  TABLE = 'table'

data_output_style.register_check_class()

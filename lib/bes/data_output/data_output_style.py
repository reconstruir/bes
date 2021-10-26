#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check
from bes.enum_util.checked_enum import checked_enum

class data_output_style(checked_enum):
  BRIEF = 'brief'
  JSON = 'json'
  PLAIN = 'plain'
  PPRINT = 'pprint'
  TABLE = 'table'

check.register_class(data_output_style,
                     include_seq = False,
                     cast_func = data_output_style.parse)

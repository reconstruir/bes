#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import enum

from ..system.check import check

from .checked_enum_mixin import checked_enum_mixin

class checked_enum(checked_enum_mixin, enum.Enum):
  'A Enum helper with methods for checking and parsing values'

  @classmethod
  def parse_string(clazz, s, ignore_case = True):
    'Parse a string or raise an error if it is not a valid flag or bitwise or of valid flags.'
    check.check_string(s)
    check.check_bool(ignore_case)

    value = clazz.parse_one_string(s, ignore_case)
    if value == None:
      raise ValueError(f'{clazz.__name__}: Invalid enumeration value: {s} - {type(s)}')
    return value
  
  @classmethod
  def parse_non_string(clazz, what):
    raise ValueError(f'{clazz.__name__}: Invalid enumeration value: {what} - {type(what)}')

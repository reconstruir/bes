#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import enum

from ..system.check import check

from .checked_enum_mixin import checked_enum_mixin

class checked_int_flag_enum(checked_enum_mixin, enum.IntFlag):
  'A IntFlag helper with methods for checking and parsing values'
  
  @classmethod
  def parse_string(clazz, s, ignore_case = True):
    'Parse a string or raise an error if it is not a valid flag or bitwise or of valid flags.'
    check.check_string(s)
    check.check_bool(ignore_case)
    
    parts = clazz._split_parts(s)
    result = 0
    for part in parts:
      next_value = clazz.parse_one_string(part, ignore_case)
      if next_value == None:
        raise ValueError(f'{clazz.__name__}: Invalid enumeration value: {s} - {type(s)}')
      result |= next_value
    return result

  @classmethod
  def parse_non_string(clazz, what):
    if check.is_int(what):
      return clazz(what)
    raise ValueError(f'{clazz.__name__}: Invalid enumeration value: {what} - {type(what)}')
  
  @classmethod
  def _split_parts(clazz, s):
    parts = s.split('|')
    parts = [ part.strip() for part in parts ]
    parts = [ part for part in parts if part ]
    return parts

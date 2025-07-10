#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import enum

from ..system.check import check

from .checked_enum_mixin import checked_enum_mixin

class checked_int_enum(checked_enum_mixin, enum.IntEnum):
  'A IntEnum helper with methods for checking and parsing values'

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
#    print(f'parse_non_string: what={what} - {type(what)}')
    if check.is_int(what):
      return clazz(what)
    elif isinstance(what, clazz):
      return what

    raise ValueError(f'{clazz.__name__}: Invalid enumeration value: {what} - {type(what)}')

  @classmethod
  def xparse(clazz, what, ignore_case = True):
    if check.is_int(what):
      return clazz(what)
    elif check.is_string(what):
      return clazz.parse_string(what, ignore_case = ignore_case)
    else:
      raise ValueError(f'{clazz.__name__}: Invalid enumeration value: {what} - {type(what)}')
  

  @classmethod
  def parse(clazz, value, ignore_case = True, allow_none = False):
    'Parse anything that can be converted to a checked_enum'

    # If it's already an enum member
    if isinstance(value, clazz):
      return value
    # If it's an int
    if isinstance(value, int):
      try:
        return clazz(value)
      except ValueError:
        raise ValueError(f'Invalid integer value for clazz: "{value}"')
    # If it's a string
    if isinstance(value, str):
      value = value.strip()
      # Try name lookup
      try:
        return clazz[value.upper()]
      except KeyError:
        pass
      # Try numeric conversion
      try:
        num = int(value)
        return clazz(num)
      except (ValueError, KeyError):
        pass
    raise ValueError(f'Cannot parse "{value}" as "{clazz}"')

#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from enum import IntEnum

from bes.system.compat import compat

class checked_int_enum(IntEnum):
  'A IntEnum helper with methods for checking and parsing values'

  @classmethod
  def is_valid(clazz, value):
    'Return True of value is valid.'
    if compat.is_int(value):
      return clazz.value_is_valid(value)
    elif compat.is_string(value):
      return clazz.name_is_valid(value)
    elif isinstance(value, clazz):
      return True
    else:
      raise TypeError('Invalid enumeration value type: {} - {}'.format(value, type(value)))
  
  @classmethod
  def is_valid_seq(clazz, seq):
    'Return True if all values in seq are valid enumeration values'
    for s in iter(seq):
      if clazz.is_valid(s):
        return True
    return False
    
  @classmethod
  def value_is_valid(clazz, value):
    'Return True if value is valid.'
    check.check_int(value)
    
    values = set([ item.value for item in clazz ])
    return value in values

  @classmethod
  def name_is_valid(clazz, name):
    'Return True if name is valid.'
    check.check_string(name)

    names = set([ item.name for item in clazz ])
    return name in names

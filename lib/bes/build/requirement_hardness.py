#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from enum import IntEnum

from bes.common.check import check
from bes.system.compat import compat

class requirement_hardness(IntEnum):
  # Requirement needed at runtime.  For example a dynamically linked library.
  RUN = 1

  # Requirement is tool needed at build time.  For example a compiler.
  TOOL = 2

  # Requirement needed only at build time.  For example a statically linked library.
  BUILD = 3
    
  # Requirement needed only for testing.
  TEST = 4
    
  DEFAULT = RUN

  @classmethod
  def is_valid(clazz, value):
    if compat.is_int(value):
      return clazz.value_is_valid(value)
    elif compat.is_string(value):
      return clazz.name_is_valid(value)
    elif isinstance(value, clazz):
      return True
    else:
      raise TypeError('invalid type for value: {} - {}'.format(value, type(value)))
  
  @classmethod
  def is_valid_seq(clazz, seq):
    for s in iter(seq):
      if clazz.is_valid(s):
        return True
    return False
    
  @classmethod
  def value_is_valid(clazz, value):
    values = set([ item.value for item in clazz ])
    return value in values

  @classmethod
  def name_is_valid(clazz, name):
    names = set([ item.name for item in clazz ])
    return name in names
  
check.register_class(requirement_hardness, include_seq = False)

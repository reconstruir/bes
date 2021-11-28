#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import enum

from bes.system.check import check
from bes.property.cached_class_property import cached_class_property

class checked_enum_mixin:
  'An Enum or IntEnum mixin with with methods for checking and parsing values'

  @classmethod
  def is_valid(clazz, what):
    'Return True if what is a valid value or name.'

    if isinstance(what, clazz):
        return True
    elif issubclass(clazz, enum.IntEnum):
      if check.is_int(what):
        return clazz.value_is_valid(what)
      elif check.is_string(what):
        return clazz.name_is_valid(what)
    elif issubclass(clazz, enum.Enum):
      if check.is_string(what):
        return clazz.value_is_valid(what) or clazz.name_is_valid(what)
    raise ValueError('Invalid enumeration value: {} - {}'.format(value, type(value)))
  
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

    if isinstance(value, clazz):
        return True
    elif issubclass(clazz, enum.IntEnum):
      if check.is_int(value):
        return value in clazz.values
    elif issubclass(clazz, enum.Enum):
      if check.is_string(value):
        return value in clazz.values
    raise ValueError('Invalid enumeration value: {} - {}'.format(value, type(value)))

  @cached_class_property
  def values(clazz):
    'Return a set all values.'
    return set([ item.value for item in clazz ])

  @cached_class_property
  def names(clazz):
    'Return a set all names.'
    return set([ item.name for item in clazz ])

  @cached_class_property
  def name_to_item_dict(clazz):
    'Return a dict of names to items.'
    result = {}
    for item in clazz:
      result[item.name] = item
    return result

  @cached_class_property
  def name_to_value_dict(clazz):
    'Return a dict of names to enum values.'
    result = {}
    for item in clazz:
      result[item.name] = item.value
    return result

  @cached_class_property
  def value_to_name_dict(clazz):
    'Return a dict of names to enum values.'
    result = {}
    for item in clazz:
      if not item.value in result:
        result[item.value] = set()
      result[item.value].add(item.name)
    return result
  
  @classmethod
  def name_is_valid(clazz, name):
    'Return True if name is valid.'
    check.check_string(name)

    return name in clazz.names

  @classmethod
  def parse(clazz, what):
    'Parse a string, int or enum return an enum item or raise an error if name is invalid.'
    
    try:
      if isinstance(what, clazz):
        return what
      elif issubclass(clazz, enum.IntEnum):
        if check.is_string(what):
          return clazz[what]
        elif check.is_int(what):
          return clazz(what)
      elif issubclass(clazz, enum.Enum):
        if check.is_string(what):
          if what in clazz.values:
            return clazz(what)
          elif what in clazz.name_to_item_dict:
            return clazz.name_to_item_dict[what]
    except ValueError as ex:
      pass
    raise ValueError('Invalid enumeration value: "{}" - {}'.format(what, type(what)))

  @classmethod
  def register_check_class(clazz):
    check.register_class(clazz,
                         include_seq = False,
                         cast_func = clazz.parse)
  

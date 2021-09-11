#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from enum import IntEnum

from bes.system.check import check
from bes.system.compat import compat
from bes.property.cached_class_property import cached_class_property

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
    
    return value in clazz.values

  @cached_class_property
  def values(clazz):
    'Return a set all values.'
    print('clazz={}'.format(clazz))
    return set([ item.value for item in clazz ])

  @cached_class_property
  def names(clazz):
    'Return a set all names.'
    return set([ item.name for item in clazz ])

  @cached_class_property
  def names_lower_case(clazz):
    'Return a set all names in lower case.'
    return set([ item.name.lower() for item in clazz ])

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
  def name_is_valid(clazz, name, ignore_case = False):
    'Return True if name is valid.'
    check.check_string(name)

    name = name.lower() if ignore_case else name
    names = clazz.names_lower_case if ignore_case else clazz.names
    return name in names

  @classmethod
  def parse(clazz, s, ignore_case = False):
    'Parse a string and return an enum or raise an error if name is invalid.'
    check.check_string(s)

    if not s in clazz.value_to_name_dict:
      raise ValueError('Not a valid enumeration: "{}"'.format(s))
    return clazz.value_to_name_dict[s]

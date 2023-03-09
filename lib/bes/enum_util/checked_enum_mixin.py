#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import enum

from ..common.string_util import string_util
from ..property.cached_class_property import cached_class_property
from ..system.check import check

class checked_enum_mixin:
  'An Enum or IntEnum mixin with with methods for checking and parsing values'

  @classmethod
  def is_valid(clazz, what):
    'Return True if what is a valid value or name.'

    try:
      clazz.parse(what, ignore_case = True)
      return True
    except ValueError as ex:
      pass
    return False
  
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

    return clazz.is_valid(value)
  
  @cached_class_property
  def values(clazz):
    'Return a set all values.'
    return set([ item.value for item in clazz ])

  @cached_class_property
  def names(clazz):
    'Return a set all names.'
    return set([ item.name for item in clazz ])

  @cached_class_property
  def names_lowercase(clazz):
    'Return a set all names.'
    return set([ item.name.lower() for item in clazz ])
  
  @cached_class_property
  def name_to_item_dict(clazz):
    'Return a dict of names to items.'
    result = {}
    for item in clazz:
      result[item.name] = item
    return result

  @cached_class_property
  def name_to_item_dict_lowercase(clazz):
    'Return a dict of names to items.'
    result = {}
    for item in clazz:
      result[item.name.lower()] = item
    return result
  
  @cached_class_property
  def name_to_value_dict(clazz):
    'Return a dict of names to enum values.'
    result = {}
    for item in clazz:
      result[item.name] = item.value
    return result

  @cached_class_property
  def name_to_value_dict_lowercase(clazz):
    'Return a dict of names to enum values.'
    result = {}
    for item in clazz:
      result[item.name.lower()] = item.value
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
  def parse(clazz, what, ignore_case = True):
    'Parse a string, int or enum return an enum item or raise an error if name is invalid.'
    
    if isinstance(what, clazz):
      return what
    if check.is_string(what):
      return clazz.parse_string(what, ignore_case = ignore_case)
    else:
      return clazz.parse_non_string(what)
    raise ValueError(f'{clazz.__name__}: Invalid enumeration value: {what} - {type(what)}')

  @classmethod
  def parse_list(clazz, s):
    'Parse a space separated list of strings into a list of enumerations.'
    check.check_string(s)
    
    strings = string_util.split_by_white_space(s, strip = True)
    return [ clazz.parse(x) for x in strings ]

  @classmethod
  def parse_one_string(clazz, s, ignore_case):
    'Parse a single string.'

    s2 = s.lower() if ignore_case else s
    if s2 in clazz.values:
      return clazz(s2)
    d = clazz.name_to_item_dict_lowercase if ignore_case else clazz.name_to_item_dict
    if s2 in d:
      return d[s2]
    return None
  
  @classmethod
  def register_check_class(clazz):
    check.register_class(clazz,
                         include_seq = False,
                         cast_func = clazz.parse)
  

  def __gt__(self, other):
    if isinstance(other, enum.Enum):
      return self.value > other.value
    if check.is_string(other):
      return self.__gt__(self.parse(other))
    return super(checked_enum_mixin, self).__gt__(other)

  def __eq__(self, other):
    if isinstance(other, enum.Enum):
      return self.value == other.value
    if check.is_string(other):
      return self.__eq__(self.parse(other))
    return super(checked_enum_mixin, self).__eq__(other)

  def __hash__(self):
    return hash(str(self))

#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from ..common.tuple_util import tuple_util

from ..property.cached_property import cached_property
from ..system.check import check
from ..version.semantic_version import semantic_version

from .btl_error import btl_error

class btl_desc_char(namedtuple('btl_desc_char', 'name, chars')):
  
  def __new__(clazz, name, chars):
    check.check_string(name)

    parsed_chars = clazz._parse_chars(chars)
    if not parsed_chars:
      raise btl_error(f'Invalid chars: {chars} - {type(chars)}')
    return clazz.__bases__[0].__new__(clazz, name, parsed_chars)

  @classmethod
  def _check_cast_func(clazz, obj):
    return tuple_util.cast_seq_to_namedtuple(clazz, obj)
  
  def __str__(self):
    return f'{self.name}: {self.chars_as_string}'

  @cached_property
  def as_dict(self):
    return {
      'name': self.name,
      'chars': self.chars,
    }
  
  @cached_property
  def chars_as_string(self):
    x = [ chr(c) for c in self.chars ]
    print(f'x={x}')
    return ' '.join([ chr(c) for c in self.chars ])
  
  @classmethod
  def _parse_chars(clazz, chars):
    if check.is_string(chars):
      return set([ ord(c) for c in chars ])
    elif check.is_int_set(chars):
      return chars.copy()
    elif check.is_int_seq(chars):
      return set(chars[:])
    elif check.is_int(chars):
      return set([ chars ])
    else:
      return None
  
check.register_class(btl_desc_char, include_seq = False, cast_func = btl_desc_char._check_cast_func)

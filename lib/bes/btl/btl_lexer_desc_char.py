#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from ..common.tuple_util import tuple_util

from ..property.cached_property import cached_property
from ..system.check import check
from ..version.semantic_version import semantic_version
from ..common.variable_manager import variable_manager

from .btl_error import btl_error

class btl_lexer_desc_char(namedtuple('btl_lexer_desc_char', 'name, chars')):
  
  def __new__(clazz, name, chars):
    check.check_string(name)
    assert isinstance(chars, set)
    check.check_set(chars, check.STRING_TYPES)
    
    return clazz.__bases__[0].__new__(clazz, name, chars)

  def to_dict(self):
    return {
      'name': self.name,
      'chars': sorted([ char for char in self.chars ]),
    }
  
  @classmethod
  def _check_cast_func(clazz, obj):
    return tuple_util.cast_seq_to_namedtuple(clazz, obj)
  
  def __str__(self):
    return f'{self.name}: {self.chars_to_string()}'

  @cached_property
  def as_dict(self):
    return self.to_dict()
  
  def chars_to_string(self, delimiter = ''):
    sorted_chars = sorted([ c for c in self.chars ])
    return delimiter.join(sorted_chars)

  def substituted_variables(self, variables):
    check.check_variable_manager(variables)

    sub_chars = set()
    for char in self.chars:
      sub_char = variables.substitute(char)
      sub_chars.add(sub_char)
    return btl_lexer_desc_char(self.name, sub_chars)
  
check.register_class(btl_lexer_desc_char, include_seq = False, cast_func = btl_lexer_desc_char._check_cast_func)

#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import typing

from collections import namedtuple

from bes.system.check import check
from bes.property.cached_property import cached_property
from bes.common.tuple_util import tuple_util
from bes.common.string_util import string_util

from .bcli_typing import bcli_typing

class bcli_option_desc_item(namedtuple('bcli_option_desc_item', 'name, option_type, default_value')):

  def __new__(clazz, name, option_type, default_value):
    check.check_string(name)
    #print(f'option_type={option_type} type={type(option_type)}')
    check.check(option_type, ( typing._GenericAlias, type ))
    #check.check(default_value, option_type, allow_none = True)
    if default_value != None:
      bcli_typing.check_instance(default_value, option_type)
    
    return clazz.__bases__[0].__new__(clazz, name, option_type, default_value)

  @classmethod
  def parse_text(clazz, text):
    check.check_string(text)

    parts = string_util.split_by_white_space(text, strip = True)
    num_parts = len(parts)
    if num_parts != 3:
      raise ValueError(f'Number of parts should be 3 instead of {num_parts}: "{text}"')
    name, type_str, default_str = parts
    option_type = bcli_typing.parse_type(type_str)
    # FIXME: this is super dangerous and should be replaced with not eval
    default_value = eval(default_str)
    if default_value != None:
      bcli_typing.check_instance(default_value, option_type)
    return bcli_option_desc_item(name, option_type, default_value)
  
  @classmethod
  def _check_cast_func(clazz, obj):
    if check.is_string(obj):
      return clazz.parse(obj)
    return tuple_util.cast_seq_to_namedtuple(clazz, obj)
  
#  @cached_property
#  def parsed_type(self):
#    return bcli_typing.parse_type(self.option_type)

check.register_class(bcli_option_desc_item,
                     include_seq = False,
                     cast_func = bcli_option_desc_item._check_cast_func)    

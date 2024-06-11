#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import ast
import typing

from collections import namedtuple

from bes.system.check import check
from bes.property.cached_property import cached_property
from bes.common.tuple_util import tuple_util
from bes.common.string_util import string_util

from .bcli_typing import bcli_typing
from .bcli_simple_type_item import bcli_simple_type_item
from .bcli_simple_type_manager import bcli_simple_type_manager

class bcli_option_desc_item(namedtuple('bcli_option_desc_item', 'name, option_type, default_value')):

  def __new__(clazz, name, option_type, default_value):
    check.check_string(name)
    check.check(option_type, ( type, typing._GenericAlias ))
    
    if default_value != None:
      bcli_simple_type_manager.check_instance(default_value, option_type)
    
    return clazz.__bases__[0].__new__(clazz, name, option_type, default_value)

  @classmethod
  def parse_text(clazz, manager, text):
    check.check_bcli_simple_type_manager(manager)
    check.check_string(text)

    parts = string_util.split_by_white_space(text, strip = True)
    num_parts = len(parts)
    if num_parts < 3:
      raise ValueError(f'Number of parts should be at least 3 instead of {num_parts}: "{text}"')
    name = parts.pop(0)
    type_str = parts.pop(0)
    default_str = ' '.join(parts)
    option_type = manager._parse_type_str_to_typing(type_str)
    default_value = ast.literal_eval(default_str)
    if default_value != None:
      manager.check_instance(default_value, option_type)
    return bcli_option_desc_item(name, option_type, default_value)
  
  @classmethod
  def _check_cast_func(clazz, obj):
    if check.is_string(obj):
      return clazz.parse(obj)
    return tuple_util.cast_seq_to_namedtuple(clazz, obj)
  
check.register_class(bcli_option_desc_item,
                     include_seq = False,
                     cast_func = bcli_option_desc_item._check_cast_func)    

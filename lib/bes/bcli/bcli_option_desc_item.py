#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import ast
import typing

from collections import namedtuple

from bes.system.check import check
from bes.system.log import logger
from bes.common.json_util import json_util
from bes.common.bool_util import bool_util
from bes.property.cached_property import cached_property
from bes.key_value.key_value_list import key_value_list
from bes.text.string_lexer_options import string_lexer_options
from bes.common.tuple_util import tuple_util
from bes.common.string_util import string_util

from .bcli_simple_type_item import bcli_simple_type_item
from .bcli_simple_type_manager import bcli_simple_type_manager

class bcli_option_desc_item(namedtuple('bcli_option_desc_item', 'name, option_type, default, secret')):

  _log = logger('bcli')
  
  def __new__(clazz, name, option_type, default, secret):
    check.check_string(name)
    #print(f'CACA: option_type={option_type}')
    check.check(option_type, ( type, typing._GenericAlias ))
#    if default != None:
#      bcli_simple_type_manager.check_instance(default, option_type)
    check.check_bool(secret)
    
    return clazz.__bases__[0].__new__(clazz, name, option_type, default, secret)

  def to_dict(self):
    return dict(self._asdict())
  
  def to_json(self):
    d = self.to_dict()
    d['option_type'] = str(self.option_type)
    return json_util.to_json(d, indent = 2, sort_keys = False)
  
  @classmethod
  def parse_text(clazz, manager, text):
    check.check_bcli_simple_type_manager(manager)
    check.check_string(text)

    parts = clazz._parse_parts(text)
    parsed_type = manager._parse_type_str(parts.type_str)
    typing_type = manager._parse_type_str_to_typing(parts.type_str)

    clazz._log.log_d(f'text="{text}" parts={parts} parsed_type={parsed_type}')

    #print(f'text="{text}" parts={parts} parsed_type={parsed_type}', flush = True)
    
    type_item = manager._types[parsed_type.base]

    #print(f'type_item={type_item}', flush = True)

    if 'default' in parts.values:
      default_str = parts.values['default']
      resolved_default_str = manager.substitute_variables(default_str)
      #print(f'resolved_default_str=_{resolved_default_str}_')
      #clazz._log.log_d(f'2: CACA resolved_default_str={resolved_default_str}')
      if type_item.parse_function:
        default = type_item.parse_function(resolved_default_str)
      else:
        default = ast.literal_eval(resolved_default_str)
        #print(f'default=_{default}_')
      manager.check_instance(default, typing_type)
    elif manager.has_default(parts.name):
      default = manager.default(parts.name)()
      manager.check_instance(default, typing_type)
    else:
      default = None
      
    secret = bool_util.parse_bool(parts.values.get('secret', 'False'))

    if default != None:
      manager.check_instance(default, typing_type)
    
    return bcli_option_desc_item(parts.name, typing_type, default, secret)

  _parse_parts_result = namedtuple('_parse_parts_result', 'name, type_str, values')
  @classmethod
  def _parse_parts(clazz, text):
    check.check_string(text)

    parts = string_util.split_by_white_space(text, strip = True)
    num_parts = len(parts)
    if num_parts < 2:
      raise ValueError(f'Number of parts should be at least 2 instead of {num_parts}: "{text}"')
    name = parts.pop(0)
    type_str = parts.pop(0)
    rest_text = text.replace(name, '', 1).replace(type_str, '', 1)
    kvl = key_value_list.parse(rest_text, string_lexer_options.KEEP_QUOTES).to_dict()
    return clazz._parse_parts_result(name, type_str, kvl)
  
  @classmethod
  def _check_cast_func(clazz, obj):
    if check.is_string(obj):
      return clazz.parse(obj)
    return tuple_util.cast_seq_to_namedtuple(clazz, obj)
  
check.register_class(bcli_option_desc_item,
                     include_seq = False,
                     cast_func = bcli_option_desc_item._check_cast_func)    

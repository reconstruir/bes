#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy

from collections import namedtuple

from ..common.json_util import json_util
from ..common.tuple_util import tuple_util
from ..system.check import check
from ..property.cached_property import cached_property

class btl_parser_item(namedtuple('btl_parser_item', 'name, value, tokens')):

  def __new__(clazz, name, value, tokens):
    check.check_string(name)
    check.check_string(value)
    tokens = check.check.btl_lexer_token_list(tokens)
    
    return clazz.__bases__[0].__new__(clazz, name, value, tokens)

  def __str__(self):
    return f'{self.name}:{self.value}'

  @cached_property
  def tokens_as_string(self):
    return str(self.tokens)

  def to_dict(self):
    return {
      'name': self.name,
      'value': self.value,
      'tokens': self.tokens.to_dict_list()
    }

  def to_json(self):
    return json_util.to_json(self.to_dict(), indent = 2, sort_keys = False)
  
  def clone(self, mutations = None):
    return tuple_util.clone(self, mutations = mutations)

  @classmethod
  def _check_cast_func(clazz, obj):
    return tuple_util.cast_seq_to_namedtuple(clazz, obj)
  
check.register_class(btl_parser_item, include_seq = False, cast_func = btl_parser_item._check_cast_func)
  

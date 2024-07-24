#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import ast
from collections import namedtuple

from bes.system.log import logger
from bes.system.check import check
from bes.property.cached_property import cached_property
from bes.common.tuple_util import tuple_util

class bcli_simple_type_item(namedtuple('bcli_simple_type_item', 'name, type_function, parse_function, check_function')):

  _log = logger('bcli')
  
  def __new__(clazz, name, type_function, parse_function = None, check_function = None):
    check.check_string(name)
    check.check_callable(type_function)
    check.check_callable(parse_function, allow_none = True)
    check.check_callable(check_function, allow_none = True)
    
    return clazz.__bases__[0].__new__(clazz, name, type_function, parse_function, check_function)

  @cached_property
  def type(self):
    return self.type_function()

  def parse_text(self, text):
    check.check_string(text)

    if self.parse_function:
      return self.parse_function(text)
    self._log.log_d(f'1: CACA text={text}')
    return ast.literal_eval(text)
  
  @classmethod
  def _check_cast_func(clazz, obj):
    return tuple_util.cast_seq_to_namedtuple(clazz, obj)
  
check.register_class(bcli_simple_type_item,
                     include_seq = False,
                     cast_func = bcli_simple_type_item._check_cast_func)    

#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.system.check import check
from bes.property.cached_property import cached_property

class bcli_simple_type_item(namedtuple('bcli_simple_type_item', 'name, type_function, default_function')):

  def __new__(clazz, name, type_function, default_function):
    check.check_string(name)
    check.check_callable(type_function)
    check.check_callable(default_function)
    
    return clazz.__bases__[0].__new__(clazz, name, type_function, default_function)

  @cached_property
  def type(self):
    return self.type_function()

  @cached_property
  def default(self):
    return self.default_function()
  
  @classmethod
  def _check_cast_func(clazz, obj):
    return tuple_util.cast_seq_to_namedtuple(clazz, obj)
  
check.register_class(bcli_simple_type_item,
                     include_seq = False,
                     cast_func = bcli_simple_type_item._check_cast_func)    

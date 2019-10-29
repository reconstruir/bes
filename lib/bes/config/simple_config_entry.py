#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check
from bes.key_value.key_value import key_value

from collections import namedtuple

class simple_config_entry(namedtuple('simple_config_entry', 'value, origin')):

  def __new__(clazz, value, origin):
    check.check_key_value(value)
    check.check_simple_config_origin(origin)
    return clazz.__bases__[0].__new__(clazz, value, origin)
    
  def __str__(self):
    return self.value.to_string(delimiter = ': ', quote_value = False)
  
check.register_class(simple_config_entry)

#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check
from bes.key_value.key_value import key_value

#from collections import namedtuple

class simple_config_entry(object):

  def __init__(self, value, origin):
    check.check_key_value(value)
    check.check_simple_config_origin(origin)
    self.value = value
    self.origin = origin

  def __str__(self):
    return self.value.to_string(delimiter = ': ', quote_value = False)
  
check.register_class(simple_config_entry)

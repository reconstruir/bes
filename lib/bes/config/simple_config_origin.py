#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.check import check

from collections import namedtuple

class simple_config_origin(namedtuple('simple_config_origin', 'source, line_number')):

  def __new__(clazz, source, line_number):
    check.check_string(source)
    check.check_int(line_number, allow_none = True)
    return clazz.__bases__[0].__new__(clazz, source, line_number)

  def __str__(self):
    if self.line_number == None:
      return self.source
    return '{}:{}'.format(self.source, self.line_number)
  
check.register_class(simple_config_origin)

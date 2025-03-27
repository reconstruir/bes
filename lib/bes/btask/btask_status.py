# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from ..system.check import check
from ..property.cached_property import cached_property

class btask_status(namedtuple('btask_status', 'task_id, minimum, maximum, value, message')):
  
  def __new__(clazz, task_id, minimum, maximum, value, message):
    check.check_int(task_id)
    check.check_int(minimum, allow_none = True)
    check.check_int(maximum, allow_none = True)
    check.check_int(value)
    check.check_string(message, allow_none = True)

    if maximum == None:
      if minimum != None:
        raise ValueError(f'"minimum" ({minimum}) should be None when maximum is None')
      
      if value not in ( 0, 1 ):
        raise ValueError(f'"value" should be either 0 or 1 when maximum is None: value="{value}"')
    else:
      if minimum == None:
        raise ValueError(f'"minimum" should be given if "maximum" ({maximum}) is given')

      if maximum < minimum:
        raise ValueError(f'"maximum" should be >= "minimum" : maximum="{maximum}" maximum="{maximum}"')

      if value < minimum:
        raise ValueError(f'"value" ({value}) should be >/ "minimum" {minimum}')

      if value > maximum:
        raise ValueError(f'"value" ({value}) should be <= "maximum" {maximum}')
    
    return clazz.__bases__[0].__new__(clazz, task_id, minimum, maximum, value, message)

  @cached_property
  def percent_done(self):
    if self.maximum == None:
      raise ValueError('cannot compute percent done because maximum is not given.')
    left = float(self.value - self.minimum)
    delta = float(self.maximum - self.minimum)
    return (left * 100.0) / delta
  
check.register_class(btask_status, include_seq = False)

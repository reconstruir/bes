# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from ..system.check import check
from ..property.cached_property import cached_property

class btask_progress(namedtuple('btask_progress', 'task_id, current, total, message')):
  
  def __new__(clazz, task_id, current, total, message):
    check.check_int(task_id)
    check.check_int(current)
    check.check_int(total, allow_none = True)
    check.check_string(message, allow_none = True)

    if total == None:
      if current not in ( 0, 1 ):
        raise ValueError(f'current should be either 0 or 1 when total is None: "{current}"')
    else:
      if total <= 0:
        raise ValueError(f'total should be greater than 0: "{total}"')
      
      if current <= 0:
        raise ValueError(f'current should be greater than 0: "{current}"')

      if current > total:
        raise ValueError(f'current should be <= total: "{current}"')
    
    return clazz.__bases__[0].__new__(clazz, task_id, current, total, message)

  @cached_property
  def percent_done(self):
    return float(self.current) / float(total)
  
check.register_class(btask_progress, include_seq = False)

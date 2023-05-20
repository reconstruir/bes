# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from ..system.check import check
from ..property.cached_property import cached_property

from .btask_priority import btask_priority

class btask_progress(namedtuple('btask_progress', 'current, total')):
  
  def __new__(clazz, current, total):
    check.check_int(current)
    check.check_int(total)

    if current <= 0:
      raise ValueError(f'current should be greater than 0: "{current}"')

    if total <= 0:
      raise ValueError(f'total should be greater than 0: "{total}"')
    
    if current > total:
      raise ValueError(f'current should be <= total: "{current}"')
    
    return clazz.__bases__[0].__new__(clazz, current, total)

  @cached_property
  def percent_done(self):
    return float(self.current) / float(total)
  
check.register_class(btask_progress, include_seq = False)

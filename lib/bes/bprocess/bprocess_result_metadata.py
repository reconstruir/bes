# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from ..system.check import check
from ..property.cached_property import cached_property

from .bprocess_error import bprocess_error

class bprocess_result_metadata(namedtuple('bprocess_result_metadata', 'pid, add_time, start_time, end_time')):
  
  def __new__(clazz, pid, add_time, start_time, end_time):
    check.check_int(pid, allow_none = True)
    check.check_datetime(add_time)
    check.check_datetime(start_time, allow_none = True)
    check.check_datetime(end_time)

    return clazz.__bases__[0].__new__(clazz, pid, add_time, start_time, end_time)

  @cached_property
  def duration(self):
    if not self.start_time:
      raise bprocess_error(f'task was never started')
    return self.end_time - self.start_time

  @cached_property
  def total_duration(self):
    return self.end_time - self.add_time
  
check.register_class(bprocess_result_metadata, include_seq = False)
  

# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from ..common.json_util import json_util
from ..common.tuple_util import tuple_util
from ..system.check import check
from ..property.cached_property import cached_property

from .btask_error import btask_error

class btask_result_metadata(namedtuple('btask_result_metadata', 'pid, add_time, start_time, end_time')):
  
  def __new__(clazz, pid, add_time, start_time, end_time):
    check.check_int(pid, allow_none = True)
    check.check_datetime(add_time)
    check.check_datetime(start_time, allow_none = True)
    check.check_datetime(end_time)

    return clazz.__bases__[0].__new__(clazz, pid, add_time, start_time, end_time)

  def to_dict(self):
    return {
      'pid': self.pid,
      'add_time': str(self.add_time),
      'start_time': str(self.start_time),
      'end_time': str(self.end_time),
    }

  def clone(self, mutations = None):
    return tuple_util.clone(self, mutations = mutations)
  
  def to_json(self):
    return json_util.to_json(self.to_dict(), indent = 2, sort_keys = True)
  
  @cached_property
  def duration(self):
    if not self.start_time:
      raise btask_error(f'task was never started')
    return self.end_time - self.start_time

  @cached_property
  def total_duration(self):
    return self.end_time - self.add_time
  
check.register_class(btask_result_metadata, include_seq = False)
  

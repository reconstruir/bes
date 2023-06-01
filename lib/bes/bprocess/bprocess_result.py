# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from ..system.check import check
from ..common.tuple_util import tuple_util

from .bprocess_cancelled_error import bprocess_cancelled_error
from .bprocess_error import bprocess_error
from .bprocess_result_metadata import bprocess_result_metadata
from .bprocess_result_state import bprocess_result_state

class bprocess_result(namedtuple('bprocess_result', 'task_id, state, data, metadata, error, args')):
  
  def __new__(clazz, task_id, state, data, metadata, error, args):
    check.check_int(task_id)
    state = check.check_bprocess_result_state(state)
    check.check_dict(data, allow_none = True)
    check.check_bprocess_result_metadata(metadata)
    check.check_dict(args, allow_none = True)

    return clazz.__bases__[0].__new__(clazz, task_id, state, data, metadata, error, args)

  def __str__(self):
    if self.data:
      data_str = f'{len(self.data)} bytes'
    else:
      data_str = f'None'
    return f'{{ task_id={self.task_id} state={self.state.name} data={data_str} error="{self.error}" args="{self.args}" }}'

  def __repr__(self):
    return self.__str__()
  
  def clone(self, mutations = None):
    return tuple_util.clone(self, mutations = mutations)
  
  @classmethod
  def from_dict(clazz, d):
    check.check_dict(d)
    
    if not 'task_id' in d:
      raise bprocess_error(f'no "task_id" found in d')
    if not 'state' in d:
      raise bprocess_error(f'no "state" found in d')
    if not 'data' in d:
      raise bprocess_error(f'no "data" found in d')
    if not 'metadata' in d:
      raise bprocess_error(f'no "metadata" found in d')
    
    return bprocess_result(d['task_id'],
                        d['state'],
                        d['data'],
                        d['metadata'],
                        d.get('error', None),
                        d.get('args', None))

check.register_class(bprocess_result, include_seq = False)
  

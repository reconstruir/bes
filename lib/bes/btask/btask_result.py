# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy
from collections import namedtuple

from ..common.json_util import json_util
from ..common.tuple_util import tuple_util
from ..system.check import check

from .btask_cancelled_error import btask_cancelled_error
from .btask_error import btask_error
from .btask_result_metadata import btask_result_metadata
from .btask_result_state import btask_result_state

class btask_result(namedtuple('btask_result', 'task_id, state, data, metadata, error, args')):
  
  def __new__(clazz, task_id, state, data, metadata, error, args):
    check.check_int(task_id)
    state = check.check_btask_result_state(state)
    check.check_dict(data, allow_none = True)
    check.check_btask_result_metadata(metadata)
    check.check_dict(args, allow_none = True)

    return clazz.__bases__[0].__new__(clazz,
                                      task_id,
                                      state,
                                      copy.copy(data),
                                      metadata,
                                      error,
                                      copy.copy(args))

  def __str__(self):
    if self.data:
      data_str = f'{len(self.data)} bytes'
    else:
      data_str = f'None'
    return f'{{ task_id={self.task_id} state={self.state.name} data={data_str} error="{self.error}" args="{self.args}" }}'

  def __repr__(self):
    return self.__str__()

  def to_dict(self):
    return {
      'task_id': self.task_id,
      'state': self.state.name,
      'data': self.data,
      'metadata': self.metadata.to_dict(),
      'error': self.error,
      'args': self.args,
    }
  
  def to_json(self):
    return json_util.to_json(self.to_dict(), indent = 2, sort_keys = False)
  
  def clone(self, mutations = None):
    return tuple_util.clone(self, mutations = mutations)
  
  @classmethod
  def from_dict(clazz, d):
    check.check_dict(d)
    
    if not 'task_id' in d:
      raise btask_error(f'no "task_id" found in d')
    if not 'state' in d:
      raise btask_error(f'no "state" found in d')
    if not 'data' in d:
      raise btask_error(f'no "data" found in d')
    if not 'metadata' in d:
      raise btask_error(f'no "metadata" found in d')
    
    return btask_result(d['task_id'],
                        d['state'],
                        d['data'],
                        d['metadata'],
                        d.get('error', None),
                        d.get('args', None))

check.register_class(btask_result, include_seq = False)
  

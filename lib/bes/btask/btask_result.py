# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from ..system.check import check

from .btask_error import btask_error
from .btask_result_metadata import btask_result_metadata

class btask_result(namedtuple('btask_result', 'task_id, success, data, metadata, error, args')):
  
  def __new__(clazz, task_id, success, data, metadata, error, args):
    check.check_int(task_id)
    check.check_bool(success)
    check.check_dict(data, allow_none = True)
    check.check_btask_result_metadata(metadata)
    check.check_dict(args, allow_none = True)

    return clazz.__bases__[0].__new__(clazz, task_id, success, data, metadata, error, args)

  @classmethod
  def from_dict(clazz, d):
    check.check_dict(d)
    
    if not 'task_id' in d:
      raise btask_error(f'no "task_id" found in d')
    if not 'success' in d:
      raise btask_error(f'no "success" found in d')
    if not 'data' in d:
      raise btask_error(f'no "data" found in d')
    if not 'metadata' in d:
      raise btask_error(f'no "metadata" found in d')
    
    return btask_result(d['task_id'],
                        d['success'],
                        d['data'],
                        d['metadata'],
                        d.get('error', None),
                        d.get('args', None))
  
check.register_class(btask_result, include_seq = False)
  

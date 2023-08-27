# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from ..system.check import check
from ..common.tuple_util import tuple_util

from .btask_config import btask_config

class btask_task(namedtuple('btask_task', 'task_id, function, callback, progress_callback, config, args')):
  
  def __new__(clazz, task_id, function, callback = None, progress_callback = None, config = None, args = None):
    check.check_int(task_id)
    check.check_callable(function)
    check.check_callable(callback, allow_none = True)
    check.check_callable(progress_callback, allow_none = True)
    config = check.check_btask_config(config, allow_none = True)
    check.check_dict(args, allow_none = True)

    return clazz.__bases__[0].__new__(clazz, task_id, function, callback, progress_callback, config, args)

  @classmethod
  def _check_cast_func(clazz, obj):
    return tuple_util.cast_seq_to_namedtuple(clazz, obj)
  
check.register_class(btask_task, include_seq = False, cast_func = btask_task._check_cast_func)

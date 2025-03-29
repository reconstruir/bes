#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from ..common.tuple_util import tuple_util
from ..system.log import logger
from ..system.check import check

from .btask_config import btask_config

class btask_task(namedtuple('btask_task', 'task_id, add_time, config, function, args, callback, status_callback, cancelled_value')):

  def __new__(clazz, task_id, add_time, config, function, args, callback, status_callback, cancelled_value):
    check.check_int(task_id)
    check.check_datetime(add_time)
    config = check.check_btask_config(config)
    check.check_callable(function)
    check.check_dict(args, allow_none = True)
    check.check_callable(callback, allow_none = True)
    check.check_callable(status_callback, allow_none = True)
    
    return clazz.__bases__[0].__new__(clazz,
                                      task_id,
                                      add_time,
                                      config,
                                      function,
                                      args,
                                      callback,
                                      status_callback,
                                      cancelled_value)

  def clone(self, mutations = None):
    return tuple_util.clone(self, mutations = mutations)
  
check.register_class(btask_task, include_seq = False)

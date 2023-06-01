#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.system.log import logger
from bes.system.check import check

from .bprocess_config import bprocess_config

class bprocess_pool_item(namedtuple('bprocess_pool_item', 'task_id, add_time, config, function, args, callback, progress_callback, cancelled')):
  
  def __new__(clazz, task_id, add_time, config, function, args, callback, progress_callback, cancelled):
    check.check_int(task_id)
    check.check_datetime(add_time)
    check.check_bprocess_config(config)
    check.check_callable(function)
    check.check_dict(args, allow_none = True)
    check.check_callable(callback, allow_none = True)
    check.check_callable(progress_callback, allow_none = True)
    
    return clazz.__bases__[0].__new__(clazz,
                                      task_id,
                                      add_time,
                                      config,
                                      function,
                                      args,
                                      callback,
                                      progress_callback,
                                      cancelled)

check.register_class(bprocess_pool_item, include_seq = False)

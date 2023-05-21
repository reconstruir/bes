#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.system.log import logger
from bes.system.check import check

from .btask_config import btask_config

class btask_pool_item(namedtuple('btask_pool_item', 'task_id, add_time, config, function, callback, progress_callback, interrupted')):
  
  def __new__(clazz, task_id, add_time, config, function, callback, progress_callback, interrupted):
    check.check_int(task_id)
    check.check_datetime(add_time)
    check.check_btask_config(config)
    check.check_callable(function)
    check.check_callable(callback, allow_none = True)
    check.check_callable(progress_callback, allow_none = True)
    
    return clazz.__bases__[0].__new__(clazz, task_id, add_time, config, function, callback, progress_callback, interrupted)

  @property
  def task_args(self):
    return ( self.task_id, self.function, self.add_time, self.config.debug )

check.register_class(btask_pool_item, include_seq = False)

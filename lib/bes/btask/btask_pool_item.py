#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from datetime import datetime
import multiprocessing

from bes.system.log import logger
from bes.system.check import check

from .btask_error import btask_error
from .btask_priority import btask_priority
from .btask_result import btask_result
from .btask_result_metadata import btask_result_metadata
from .btask_threading import btask_threading
from .btask_config import btask_config

class btask_pool_item(namedtuple('btask_pool_item', 'task_id, add_time, task_args, config, function, callback, progress_callback, interrupted_value')):
  
  def __new__(clazz, task_id, add_time, task_args, config, function, callback, progress_callback, interrupted_value):
    check.check_int(task_id)

    return clazz.__bases__[0].__new__(clazz, task_id, add_time, task_args, config, function, callback, progress_callback, interrupted_value)
  
check.register_class(btask_pool_item, include_seq = False)

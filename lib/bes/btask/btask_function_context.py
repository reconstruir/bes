#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.system.log import logger
from bes.system.check import check

class btask_function_context(namedtuple('btask_function_context', 'task_id, progress_queue, interrupted')):
  
  def __new__(clazz, task_id, progress_queue, interrupted):
    check.check_int(task_id)
    
    return clazz.__bases__[0].__new__(clazz, task_id, progress_queue, interrupted)

check.register_class(btask_function_context, include_seq = False)

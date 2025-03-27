#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.system.log import logger
from bes.system.check import check

from .btask_cancelled_error import btask_cancelled_error
from .btask_status import btask_status

class btask_function_context(namedtuple('btask_function_context', 'task_id, progress_queue, cancelled_value')):
  
  def __new__(clazz, task_id, progress_queue, cancelled_value):
    check.check_int(task_id)
    
    return clazz.__bases__[0].__new__(clazz, task_id, progress_queue, cancelled_value)

  def was_cancelled(self):
    return self.cancelled_value.value

  def raise_cancelled_if_needed(self, message):
    if self.was_cancelled():
      raise btask_cancelled_error(message)

  def report_status(self, minimum, maximum, value, message):
    progress = btask_status(task_id = self.task_id,
                            minimum = minimum,
                            maximum = maximum,
                            value = value,
                            message = message)
    self.progress_queue.put(progress)
    
check.register_class(btask_function_context, include_seq = False)

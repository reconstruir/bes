#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.system.log import logger
from bes.system.check import check

from .btask_cancelled_error import btask_cancelled_error
from .btask_status_progress import btask_status_progress
from .btask_progress import btask_progress

class btask_function_context(namedtuple('btask_function_context', 'task_id, progress_queue, cancelled_value')):

  _log = logger('btask')
  
  def __new__(clazz, task_id, progress_queue, cancelled_value):
    check.check_int(task_id)
    
    return clazz.__bases__[0].__new__(clazz, task_id, progress_queue, cancelled_value)

  def was_cancelled(self):
    return self.cancelled_value.value

  def raise_cancelled_if_needed(self, message):
    if self.was_cancelled():
      raise btask_cancelled_error(message)

  def report_status(self, status):
    check.check_btask_status(status)
    self.progress_queue.put(status)

  def report_progress(self, minimum, maximum, value, message):
    progress = btask_progress(minimum = minimum,
                              maximum = maximum,
                              value = value,
                              message = message)
    status = btask_status_progress(task_id = self.task_id, progress = progress)
    self.report_status(status)
    
check.register_class(btask_function_context, include_seq = False)

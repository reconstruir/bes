#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.system.log import logger
from bes.system.check import check

from .bprocess_cancelled_error import bprocess_cancelled_error
from .bprocess_progress import bprocess_progress

class bprocess_function_context(namedtuple('bprocess_function_context', 'task_id, progress_queue, cancelled_value')):
  
  def __new__(clazz, task_id, progress_queue, cancelled_value):
    check.check_int(task_id)
    
    return clazz.__bases__[0].__new__(clazz, task_id, progress_queue, cancelled_value)

  def was_cancelled(self):
    return self.cancelled_value.value

  def raise_cancelled_if_needed(self, message):
    if self.was_cancelled():
      raise bprocess_cancelled_error(message)

  def report_progress(self, minimum, maximum, value, message):
    progress = bprocess_progress(self.task_id, minimum, maximum, value, message)
    self.progress_queue.put(progress)
    
check.register_class(bprocess_function_context, include_seq = False)

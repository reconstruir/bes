#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.system.log import logger
from bes.system.check import check

from .btask_cancelled_error import btask_cancelled_error
from .btask_status_progress import btask_status_progress
from .btask_progress import btask_progress
from .btask_step_progress import btask_step_progress
from .btask_status_step_progress import btask_status_step_progress
from ._btask_status_queue_item import _btask_status_queue_item
from .btask_status import btask_status

class btask_function_context(namedtuple('btask_function_context', 'task_id, status_queue, cancelled_value')):

  _log = logger('btask')
  _STEP_THROTTLE_WARN_THRESHOLD = 100

  def __new__(clazz, task_id, status_queue, cancelled_value):
    check.check_int(task_id)

    instance = clazz.__bases__[0].__new__(clazz, task_id, status_queue, cancelled_value)
    instance._last_step_report = None
    instance._step_drop_count = 0
    return instance

  def was_cancelled(self):
    return self.cancelled_value.value

  def raise_cancelled_if_needed(self, message):
    if self.was_cancelled():
      raise btask_cancelled_error(message)

  def report_status(self, status):
    check.check_btask_status(status)
    
    self.status_queue.put(_btask_status_queue_item(self.task_id, status))

  def report_progress(self, minimum, maximum, value, message):
    progress = btask_progress(minimum = minimum,
                              maximum = maximum,
                              value = value,
                              message = message)
    status = btask_status_progress(progress = progress)
    self.report_status(status)

  def report_step_progress(self, step, total_steps, step_title, step_percent = None):
    check.check_int(step)
    check.check_int(total_steps, allow_none = True)
    check.check_string(step_title)
    check.check_int(step_percent, allow_none = True)

    key = (step, total_steps, step_percent)
    if key == self._last_step_report:
      self._step_drop_count += 1
      if self._step_drop_count == self._STEP_THROTTLE_WARN_THRESHOLD:
        self._log.log_w(f'report_step_progress: auto-throttled {self._step_drop_count} identical '
                        f'calls for step={step} step_percent={step_percent} - caller is reporting '
                        f'too frequently, consider reducing call frequency')
      return

    self._last_step_report = key
    self._step_drop_count = 0

    sp = btask_step_progress(step = step,
                             total_steps = total_steps,
                             step_title = step_title,
                             step_percent = step_percent)
    self.report_status(btask_status_step_progress(step_progress = sp))

check.register_class(btask_function_context, include_seq = False)

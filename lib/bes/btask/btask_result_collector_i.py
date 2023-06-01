#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import threading
import time

from bes.system.log import logger
from bes.system.check import check
from abc import abstractmethod, ABCMeta
from bes.system.compat import with_metaclass

from .btask_result import btask_result
from .btask_progress import btask_progress
from .btask_error import btask_error

class btask_result_collector_i(with_metaclass(ABCMeta, object)):

  _log = logger('btask')

  def __init__(self, queue, progress_sleep_time = 0):#.025):
    self._queue = queue
    self._thread = None
    self._progress_sleep_time = progress_sleep_time

  @abstractmethod
  def handle_result(self, result):
    raise NotImplemented('handle_result')

  @abstractmethod
  def handle_progress(self, progress):
    raise NotImplemented('handle_progress')
  
  def _result_collector_thread_main(self):
    i = 0
    while True:
      self._log.log_d(f'_result_collector_thread_main:{i} calling get...')
      item = self._queue.get()
      task_id = item.task_id if item else 'None'
      self._log.log_d(f'_result_collector_thread_main:{i} got item task_id={task_id} - {type(item)}')
      if self._handle_item(item):
        break
      i += 1

  def _handle_item(self, item):
    if item == None:
      return True
    if isinstance(item, btask_result):
      self.handle_result(item)
    elif isinstance(item, btask_progress):
      self.handle_progress(item)
      time.sleep(self._progress_sleep_time)
    else:
      raise btask_error(f'got unexpected item from queue: "{item}" - {type(item)}')
      return False
  
  def start(self):
    if self._thread:
      return
    self._thread = threading.Thread(target = self._result_collector_thread_main,
                                    args = (),
                                    name = 'btask_collector')
    self._thread.start()

  def stop(self):
    if not self._thread:
      return
    self._queue.put(None)
    self._thread.join()
    self._thread = None
    
check.register_class(btask_result_collector_i, name = 'btask_result_collector', include_seq = False)

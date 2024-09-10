#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import threading
import time
import multiprocessing
import queue

from bes.system.log import logger
from bes.system.check import check
from abc import abstractmethod, ABCMeta

from .bprocess_result import bprocess_result
from .bprocess_progress import bprocess_progress
from .bprocess_error import bprocess_error

class bprocess_result_collector_i(object, metaclass = ABCMeta):

  _log = logger('bprocess')

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
      valid, item = self._get_item()
      if not valid:
        continue
      if not item:
        break
      task_id = item.task_id if item else 'None'
      self._log.log_d(f'_result_collector_thread_main:{i} got item task_id={task_id} - {type(item)}')
      self._handle_item(item)
      self._queue.task_done()
      i += 1

  def _get_item(self):
    try:
      #item = self._queue.get(timeout = 0.001)
      item = self._queue.get()
      return True, item
    except Exception as ex:
      return False, None
      
  def _handle_item(self, item):
    assert item != None
    if isinstance(item, bprocess_result):
      self.handle_result(item)
    elif isinstance(item, bprocess_progress):
      self.handle_progress(item)
      time.sleep(self._progress_sleep_time)
    else:
      raise bprocess_error(f'got unexpected item from queue: "{item}" - {type(item)}')
  
  def start(self):
    if self._thread:
      return
    self._thread = threading.Thread(target = self._result_collector_thread_main,
                                    args = (),
                                    name = 'bprocess_collector')
    self._thread.start()

  def stop(self):
    if not self._thread:
      return
    self._queue.put(None)
    self._thread.join()
    self._thread = None
    
check.register_class(bprocess_result_collector_i, name = 'bprocess_result_collector', include_seq = False)

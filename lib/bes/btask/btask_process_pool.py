#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os

from collections import namedtuple
from datetime import datetime
import multiprocessing
import threading

from bes.system.log import logger
from bes.system.check import check

from .btask_cancelled_error import btask_cancelled_error
from .btask_config import btask_config
from .btask_error import btask_error
from .btask_function_context import btask_function_context
from .btask_task import btask_task
from .btask_process_task import btask_process_task
from .btask_processor_queue import btask_processor_queue
from .btask_priority import btask_priority
from .btask_result import btask_result
from .btask_result_metadata import btask_result_metadata
from .btask_result_state import btask_result_state
from .btask_threading import btask_threading
from .btask_dedicated_category_config import btask_dedicated_category_config
from .btask_process import btask_process
from .btask_initializer import btask_initializer

class _process_pool_item(namedtuple('_process_pool_item', 'task, callback')):

  def __new__(clazz, task, callback):
    check.check_btask_task(task)
    check.check_callable(callback)
    
    return clazz.__bases__[0].__new__(clazz, task, callback)

class btask_process_pool(object):

  _log = logger('btask')

  def __init__(self, num_processes, initializer = None):
    check.check_int(num_processes)
    initializer = check.check_btask_initializer(initializer, allow_none = True)
    
    self._num_processes = num_processes
    self._initializer = initializer
    self._manager = multiprocessing.Manager()
    self._input_queue = self._manager.Queue()
    self._process_result_queue = self._manager.Queue()
    self._worker_number_lock = self._manager.Lock()
    self._worker_number_value = self._manager.Value(int, 1)
    self._processes = None
    self._result_thread = None
    self._task_callbacks = {}
    self._task_callbacks_lock = multiprocessing.Lock()

  @classmethod
  def _result_thread_main(clazz, result_queue, task_callbacks, task_callbacks_lock):
    clazz._log.log_d(f'_result_thread_main:')
    while True:
      next_result = result_queue.get()
      if next_result == None:
        clazz._log.log_d(f'_result_thread_main: got the termination sentinel')
        break
      task_id = next_result.task_id
      clazz._log.log_d(f'_result_thread_main: got next_result with task_id={task_id}')
      if not isinstance(next_result, btask_result):
        clazz._log.log_e(f'_result_thread_main: got unexpected type "{type(next_result)}" instead of btask_error for task {task_id}')
        with task_callbacks_lock as lock:
          if task_id in task_callbacks:
            del task_callbacks[task_id]
        continue

      callback = None
      with task_callbacks_lock as lock:
        if not task_id in task_callbacks:
          clazz._log.log_e(f'_result_thread_main: task {task_id} not found.')
          continue
        callback = task_callbacks[task_id]
        del task_callbacks[task_id]
      assert callback != None
      callback(next_result)

  @classmethod
  def _result_thread_start(clazz, target, result_queue, task_callbacks, task_callbacks_lock):
    args = ( result_queue, task_callbacks, task_callbacks_lock )
    thread = threading.Thread(target = target, args = args)
    thread.start()
    return thread

  @classmethod
  def _result_thread_stop(clazz, thread, result_queue):
    result_queue.put(None)
    thread.join()
  
  def _processes_start(self):
    processes = []
    for i in range(1, self._num_processes + 1):
      name = f'worker-{i}'
      process = btask_process(name,
                              self._input_queue,
                              self._process_result_queue,
                              nice_level = None,
                              initializer = self._initializer)
      processes.append(process)
    for process in processes:
      process.start()
    return processes

  @classmethod
  def _processes_stop(self, processes, input_queue):
    for _ in processes:
      input_queue.put(None)
    for process in processes:
      self._log.log_i(f'_processes_stop: joining process {process.name}')
      process.join()
  
  def start(self):
    if self._processes:
      self._log.log_d(f'start: pool_caca already started')
      return
    self._processes = self._processes_start()
    self._result_thread = self._result_thread_start(self._result_thread_main,
                                                    self._process_result_queue,
                                                    self._task_callbacks,
                                                    self._task_callbacks_lock)

  def stop(self):
    if not self._processes:
      self._log.log_d(f'stop: pool_caca not started')
      return
    self._result_thread_stop(self._result_thread, self._process_result_queue)
    self._result_thread = None
    self._processes_stop(self._processes, self._input_queue)
    self._processes = None
      
  @property
  def num_processes(self):
    return self._num_processes

  def add_task(self, task, callback):
    check.check_btask_task(task)

    task_id = task.task_id
    with self._task_callbacks_lock as lock:
      if task_id in self._task_callbacks:
        raise btask_error(f'Task {task_id} is already in process.')
      self._task_callbacks[task_id] = callback
    process_task = btask_process_task(task.task_id,
                                      task.add_time,
                                      task.config,
                                      task.function,
                                      task.args,
                                      task.cancelled_value)
    self._input_queue.put(process_task)
  
check.register_class(btask_process_pool, include_seq = False)

#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os

from collections import namedtuple
from datetime import datetime
import multiprocessing
import threading

from bes.system.log import logger
from bes.system.check import check

from .btask_error import btask_error
from .btask_task import btask_task
from .btask_process_task import btask_process_task
from .btask_result import btask_result
from .btask_status_base import btask_status_base
from .btask_threading import btask_threading
from .btask_process import btask_process
from .btask_initializer import btask_initializer

class btask_process_pool(object):

  _log = logger('btask')

  def __init__(self, name, num_processes, manager, initializer = None):
    check.check_string(name)
    check.check_int(num_processes)
    initializer = check.check_btask_initializer(initializer, allow_none = True)
    self._log.log_method_d()
    self._name = name
    self._num_processes = num_processes
    self._initializer = initializer
    self._manager = manager
    self._input_queue = self._manager.Queue()
    self._process_result_queue = self._manager.Queue()
    self._worker_number_lock = self._manager.Lock()
    self._worker_number_value = self._manager.Value(int, 1)
    self._processes = None
    self._result_thread = None
    self._task_callbacks = {}
    self._task_callbacks_lock = threading.Lock()

  @classmethod
  def _result_thread_main(clazz, result_queue, task_callbacks, task_callbacks_lock, name):
    btask_threading.set_current_thread_name(f'{name}_result_thread')
    clazz._log.log_d(f'_result_thread_main:')
    while True:
      next_result = result_queue.get()
      if next_result == None:
        clazz._log.log_d(f'_result_thread_main: got the termination sentinel')
        break
      task_id = next_result.task_id
      is_result = isinstance(next_result, btask_result)
      is_progress = isinstance(next_result, btask_status_base)
      type_name = type(next_result).__name__
      clazz._log.log_d(f'_result_thread_main: got next_result with task_id={task_id} type={type_name}')
      if not (is_result or is_progress):
        clazz._log.log_e(f'_result_thread_main: got unexpected type "{type_name}" instead of btask_result or btask_status_base task_id={task_id}')
        continue
      callback = None
      with task_callbacks_lock as lock:
        if not task_id in task_callbacks:
          clazz._log.log_e(f'_result_thread_main: task {task_id} not found.')
          continue
        callback = task_callbacks[task_id]
        if is_result:
          del task_callbacks[task_id]
      assert callback != None
      callback(next_result)

  @classmethod
  def _result_thread_start(clazz, target, result_queue, task_callbacks, task_callbacks_lock, name):
    args = ( result_queue, task_callbacks, task_callbacks_lock, name )
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
      process_name = f'{self._name}_worker_{i}'
      process = btask_process(process_name,
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
                                                    self._task_callbacks_lock,
                                                    self._name)

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
    check.check_callable(callback)

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

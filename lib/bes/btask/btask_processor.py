#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os

from collections import namedtuple
from datetime import datetime
import multiprocessing

from bes.system.log import logger
from bes.system.check import check

from .btask_cancelled_error import btask_cancelled_error
from .btask_config import btask_config
from .btask_error import btask_error
from .btask_function_context import btask_function_context
from .btask_task import btask_task
from .btask_processor_queue import btask_processor_queue
from .btask_priority import btask_priority
from .btask_result import btask_result
from .btask_progress import btask_progress
from .btask_result_metadata import btask_result_metadata
from .btask_result_state import btask_result_state
from .btask_threading import btask_threading
from .btask_dedicated_category_config import btask_dedicated_category_config
from .btask_process_pool import btask_process_pool
from .btask_initializer import btask_initializer

class btask_processor(object):

  _log = logger('btask')

  def __init__(self, name, num_processes, dedicated_categories = None):
    check.check_string(name)
    check.check_int(num_processes)
    check.check_dict(dedicated_categories, allow_none = True)

    dedicated_categories = self._check_dedicated_categories(dedicated_categories)
    if dedicated_categories:
      sum_category_processes = 0
      for category, config in dedicated_categories.items():
        sum_category_processes += config.num_processes
      if sum_category_processes > num_processes:
        raise ValueError(f'The sum of dedicated category number of process ({sum_category_processes}) is more than num_processes ({num_processes})')
    
    self._name = name
    self._num_processes = num_processes
    self._dedicated_categories = dedicated_categories
    self._manager = multiprocessing.Manager()
    self._worker_number_lock = self._manager.Lock()
    self._worker_number_value = self._manager.Value(int, 1)
    self._pools = {}
    count = self._num_processes
    if dedicated_categories:
      for category, config in dedicated_categories.items():
        config = check.check_btask_dedicated_category_config(config)
        initializer_args = (
          self._worker_number_lock,
          self._worker_number_value,
          config.nice,
          config.initializer,
          config.initializer_args
        )
        initializer = btask_initializer(self._worker_initializer, initializer_args)
        pool_name = f'{name}_{category}_pool'
        pool = btask_process_pool(pool_name, config.num_processes, self._manager, initializer = initializer)
        self._pools[category] = pool
        count = count - config.num_processes
        assert count >= 0
    if count > 0:
      initializer_args = (
        self._worker_number_lock,
        self._worker_number_value,
        None,
        None,
        None
      )
      initializer = btask_initializer(self._worker_initializer, initializer_args)
      pool = btask_process_pool(f'{name}_main_pool', count, self._manager, initializer = initializer)
      self._pools['__main'] = pool
    self._result_queue = self._manager.Queue()
    self._lock = self._manager.Lock()
    self._waiting_queue = btask_processor_queue()
    self._in_progress_queue = btask_processor_queue()
    self._category_limits = {}
    self._start()

  @classmethod
  def _check_dedicated_categories(clazz, d):
    if not d:
      return None
    result = {}
    for category, v in d.items():
      check.check_string(category)
      config = check.check_btask_dedicated_category_config(v)
      result[category] = config
    return result
  
  @property
  def num_processes(self):
    return self._num_processes
    
  @property
  def result_queue(self):
    return self._result_queue

  @classmethod
  def _worker_initializer(clazz, worker_number_lock, worker_number_value, nice, initializer, initializer_args):
    with worker_number_lock as lock:
      worker_number = worker_number_value.value
      worker_number_value.value += 1
    worker_name = f'btask_worker_{worker_number}'
    btask_threading.set_current_process_name(worker_name)
    process_name = btask_threading.current_process_name()
    if nice != None:
      old_nice = os.nice(0)
      new_nice = os.nice(nice)
      clazz._log.log_i(f'{worker_name}: changed nice from {old_nice} to {new_nice}')
    if initializer:
      initializer(*(initializer_args or ()))

  def _start(self):
    if not self._pools:
      return
    for _, pool in self._pools.items():
      pool.start()
    import time
#    time.sleep(5)
      
  def stop(self):
    if not self._pools:
      return
    for _, pool in self._pools.items():
      pool.stop()
      
  def _pool_for_category(self, category):
    if self._dedicated_categories and category in self._dedicated_categories:
      target_category = category
    else:
      target_category = '__main'
    assert target_category in self._pools
    result = self._pools[target_category]
    self._log.log_i(f'_pool_for_category: category={category} result={target_category}')
    return result
    
  _task_id = 1
  def add_task(self, function, callback = None, progress_callback = None, config = None, args = None):
    check.check_callable(function)
    check.check_callable(callback, allow_none = True)
    check.check_callable(progress_callback, allow_none = True)
    config = check.check_btask_config(config, allow_none = True)
    check.check_dict(args, allow_none = True)

    config = config or btask_config(function.__name__)

    btask_threading.check_main_process(label = 'btask.add_task')

    if not config.category in self._category_limits:
      self._category_limits[config.category] = config.limit
    else:
      old_limit = self._category_limits[config.category]
      if old_limit != config.limit:
        raise btask_error(f'Trying to change the category limit for "{config.category}" from  {old_limit} to {config.limit}')

    add_time = datetime.now()
    cancelled = self._manager.Value(bool, False)
    with self._lock as lock:
      task_id = self._task_id
      self._task_id += 1
      item = btask_task(task_id,
                        add_time,
                        config,
                        function,
                        args,
                        callback,
                        progress_callback,
                        cancelled)
      self._waiting_queue.add(item)
    self._log.log_d(f'add: calling pump for task_id={task_id}')
    self._pump()
    return task_id

  _pump_iteration = 0
  def _pump(self):
    with self._lock as lock:
      self._pump_i()

  def _pump_i(self):
    self._pump_iteration += 1
    label = f'_pump:{self._pump_iteration}'
    for category, limit in self._category_limits.items():
      while self._pump_item_i(label, category, limit):
        pass

  def _pump_item_i(self, label, category, limit):
    in_progress_count = self._in_progress_queue.category_count(category)
    self._log.log_d(f'{label}: category={category} limit={limit} in_progress_count={in_progress_count}')
    if in_progress_count >= limit:
      return False
    task = self._waiting_queue.remove_by_category(category)
    if not task:
      return False
    assert isinstance(task, btask_task)
    self._log.log_d(f'{label}: got task task_id={task.task_id}')
    self._in_progress_queue.add(task)
    self._log.log_d(f'{label}: calling apply_async for task_id={task.task_id}')
    pool = self._pool_for_category(category)
    assert pool
    pool.add_task(task, self._callback)
    return True
          
  def _callback(self, result):
    check.check(result, ( btask_result, btask_progress ))

    self._log.log_d(f'_callback: result={result} queue={self._result_queue}')
    self._result_queue.put(result)
    self._log.log_d(f'_callback: calling pump for task_id={result.task_id}')
    self._pump()
    
  def complete(self, result):
    check.check_btask_result(result)

    self._log.log_d(f'complete: task_id={result.task_id}')
    
    btask_threading.check_main_process(label = 'btask.complete')
    
    with self._lock as lock:
      item = self._in_progress_queue.remove_by_task_id(result.task_id)
      if not item:
        item = self._waiting_queue.remove_by_task_id(result.task_id)
      if not item:
        self._log.log_d(f'No task_id "{result.task_id}" found to complete')
        return
      self._log.log_d(f'pump: removed task_id={result.task_id}')
      callback = item.callback
      self._pump_i()
    callback_name = callback.__name__ if callback else 'None'
    self._log.log_d(f'complete: callback={callback_name}')
    if callback:
      callback(result)

  _cancel_count = 1
  def cancel(self, task_id):
    check.check_int(task_id)
    
    btask_threading.check_main_process(label = 'btask.cancel')

    cancelled = None
    with self._lock as lock:
      self._log.log_d(f'cancel: task_id={task_id} cancel_count={self._cancel_count}')
      self._cancel_count += 1
      #assert self._cancel_count == 2
      waiting_item = self._waiting_queue.find_by_task_id(task_id)
      if waiting_item:
        self._log.log_d(f'cancel: task {task_id} removed from waiting queue')
        metadata = btask_result_metadata(None,
                                            waiting_item.add_time,
                                            None,
                                            datetime.now())
        result = btask_result(waiting_item.task_id, btask_result_state.CANCELLED, None, metadata, None, waiting_item.args)
        self._result_queue.put(result)
      in_progress_item = self._in_progress_queue.find_by_task_id(task_id)
      if not in_progress_item:
        self._log.log_d(f'cancel: no task {task_id} found in either waiting or in_progress queues')
        return
      self._log.log_d(f'cancel: task {task_id} removed from in_progress queue')
      in_progress_item.cancelled_value.value = True

  def report_progress(self, progress, raise_error = True):
    check.check_btask_progress(progress)
    check.check_bool(raise_error)

    self._log.log_d(f'report_progress: task_id={progress.task_id}')
    
    btask_threading.check_main_process(label = 'btask.report_progress')
    
    with self._lock as lock:
      item = self._in_progress_queue.find_by_task_id(progress.task_id)
      if not item:
        if not raise_error:
          return
        btask_error(f'No task_id "{progress.task_id}" found to cancel')
      progress_callback = item.progress_callback
      if progress_callback:
        progress_callback(progress)
      
  def is_cancelled(self, task_id, raise_error = True):
    check.check_int(task_id)
    check.check_bool(raise_error)

    self._log.log_d(f'is_cancelled: task_id={task_id}')
    
    with self._lock as lock:
      item = self._in_progress_queue.find_by_task_id(task_id)
      if not item:
        if not raise_error:
          return False
        btask_error(f'No task_id "{task_id}" found to check for interruption')
      return item.cancelled_value.value
      
check.register_class(btask_processor, include_seq = False)

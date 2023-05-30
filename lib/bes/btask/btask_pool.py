#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from datetime import datetime
import multiprocessing

from bes.system.log import logger
from bes.system.check import check

from .btask_cancelled_error import btask_cancelled_error
from .btask_config import btask_config
from .btask_error import btask_error
from .btask_function_context import btask_function_context
from .btask_pool_item import btask_pool_item
from .btask_pool_queue import btask_pool_queue
from .btask_priority import btask_priority
from .btask_result import btask_result
from .btask_result_metadata import btask_result_metadata
from .btask_result_state import btask_result_state
from .btask_threading import btask_threading

class btask_pool(object):

  _log = logger('btask')

  def __init__(self, num_processes):
    check.check_int(num_processes)

    self._manager = multiprocessing.Manager()
    self._worker_number_lock = self._manager.Lock()
    self._worker_number_value = self._manager.Value(int, 1)
    self._pool = multiprocessing.Pool(num_processes,
                                      initializer = self._worker_initializer,
                                      initargs = ( self._worker_number_lock, self._worker_number_value ))
    self._result_queue = self._manager.Queue()
    self._lock = self._manager.Lock()
    self._waiting_queue = btask_pool_queue()
    self._in_progress_queue = btask_pool_queue()
    self._category_limits = {}

  @property
  def result_queue(self):
    return self._result_queue

  @classmethod
  def _worker_initializer(clazz, worker_number_lock, worker_number_value):
    with worker_number_lock as lock:
      worker_number = worker_number_value.value
      worker_number_value.value += 1
    worker_name = f'btask_worker_{worker_number}'
    btask_threading.set_current_process_name(worker_name)
    process_name = btask_threading.current_process_name()
  
  def close(self):
    if not self._pool:
      return
    self._pool.terminate()
    self._pool.join()
    
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
      item = btask_pool_item(task_id,
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
      #waiting_count = self._waiting_queue.category_count(category)
      in_progress_count = self._in_progress_queue.category_count(category)
      self._log.log_d(f'{label}: category={category} limit={limit} in_progress_count={in_progress_count}')
      if in_progress_count < limit:
        item = self._waiting_queue.remove_by_category(category)
        if item:
          self._log.log_d(f'{label}: got item task_id={item.task_id}')
          self._in_progress_queue.add(item)
          self._log.log_d(f'{label}: calling apply_async for task_id={item.task_id}')
          args = (
            item.task_id,
            item.function,
            item.add_time,
            item.config.debug,
            item.args,
            self._result_queue,
            item.cancelled,
          )
          self._pool.apply_async(self._function,
                                 args = args,
                                 callback = self._callback,
                                 error_callback = self._error_callback)
            
  @classmethod
  def _function(clazz, task_id, function, add_time, debug, args, progress_queue, cancelled):
    clazz._log.log_d(f'_function: task_id={task_id} function={function}')
    start_time = datetime.now()
    error = None
    data = None
    try:
      context = btask_function_context(task_id, progress_queue, cancelled)
      data = function(context, args)
      #clazz._log.log_d(f'_function: task_id={task_id} data={data}')
      if not check.is_dict(data):
        raise btask_error(f'Function "{function}" should return a dict: "{data}" - {type(data)}')
      state = btask_result_state.SUCCESS
    except Exception as ex:
      if debug:
        clazz._log.log_exception(ex)
      if isinstance(ex, btask_cancelled_error):
        state = btask_result_state.CANCELLED
        error = None
      else:
        state = btask_result_state.FAILED
        error = ex
    end_time = datetime.now()
    clazz._log.log_d(f'_function: task_id={task_id} state={state}')
    metadata = btask_result_metadata(btask_threading.current_process_pid(),
                                     add_time,
                                     start_time,
                                     end_time)
    result = btask_result(task_id, state, data, metadata, error, args)
    #clazz._log.log_d(f'_function: result={result}')
    return result

  def _callback(self, result):
    check.check_btask_result(result)

    self._log.log_d(f'_callback: result={result} queue={self._result_queue}')
    self._result_queue.put(result)
    self._log.log_d(f'_callback: calling pump for task_id={result.task_id}')
    self._pump()
    
  def _error_callback(self, error):
    self._log.log_e(f'unexpected error: "{error}"')
    self._log.log_exception(error)
    raise btask_error(f'unexpected error: "{error}"')
    
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

  def cancel(self, task_id):
    check.check_int(task_id)

    self._log.log_d(f'cancel: task_id={task_id}')
    
    btask_threading.check_main_process(label = 'btask.cancel')

    cancelled = None
    with self._lock as lock:
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
      in_progress_item.cancelled.value = True

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
      return item.cancelled.value
      
check.register_class(btask_pool, include_seq = False)

#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from datetime import datetime
import multiprocessing

from bes.system.log import logger
from bes.system.check import check

from .btask_error import btask_error
from .btask_priority import btask_priority
from .btask_result import btask_result
from .btask_result_metadata import btask_result_metadata
from .btask_threading import btask_threading
from .btask_config import btask_config

class btask_pool(object):

  _log = logger('btask')

  def __init__(self, num_processes):
    check.check_int(num_processes)

    self._pool = multiprocessing.Pool(num_processes)
    self._manager = multiprocessing.Manager()
    self._queue = self._manager.Queue()
    self._lock = self._manager.Lock()

  @property
  def queue(self):
    return self._queue

  def close(self):
    if not self._pool:
      return
    self._pool.close()
    self._pool.join()
    
  _task_item = namedtuple('_task_item', 'task_id, task_args, config, callback, progress_callback, interrupted_value')
  _tasks = {}
  _task_id = 1
  _category_limits = {}
  _task_queues = {}

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
      if self._category_limits[config.category] != config.limit:
        btask_error(f'Trying to change the No task_id "{task_id}" found to interrupt')
    
    add_time = datetime.now()

    interruped = self._manager.Value(bool, False)
    with self._lock as lock:
      task_id = self._task_id
      self._task_id += 1
      task_args = tuple([ task_id, function, add_time, config.debug, args ])
      item = self._task_item(task_id,
                             task_args,
                             config,
                             callback,
                             progress_callback,
                             interruped)
      self._tasks[task_id] = item

      self._log.log_d(f'add_task: task_args={task_args}')
      self._pool.apply_async(self._function,
                             args = task_args,
                             callback = self._callback,
                             error_callback = self._error_callback)
      return task_id
    
  def complete(self, task_id):
    check.check_int(task_id)

    self._log.log_d(f'complete: task_id={task_id}')
    
    btask_threading.check_main_process(label = 'btask.complete')
    
    with self._lock as lock:
      if not task_id in self._tasks:
        btask_error(f'No task_id "{task_id}" found to complete')
      item = self._tasks[task_id]
      callback = item.callback
      del self._tasks[task_id]
      
    self._log.log_d(f'complete: callback={callback}')
    
    return callback

  def interrupt(self, task_id, raise_error = True):
    check.check_int(task_id)
    check.check_bool(raise_error)

    self._log.log_d(f'interrupt: task_id={task_id}')
    
    btask_threading.check_main_process(label = 'btask.interrupt')
    
    with self._lock as lock:
      if not task_id in self._tasks:
        if not raise_error:
          return
        btask_error(f'No task_id "{task_id}" found to interrupt')
      item = self._tasks[task_id]
      item.interruped.value = True

  def report_progress(self, progress, raise_error = True):
    check.check_btask_progress(progress)
    check.check_bool(raise_error)

    self._log.log_d(f'report_progress: task_id={task_id}')
    
    btask_threading.check_main_process(label = 'btask.report_progress')
    
    with self._lock as lock:
      if not progress.task_id in self._tasks:
        if not raise_error:
          return
        btask_error(f'No task_id "{progress.task_id}" found to interrupt')
      item = self._tasks[progress.task_id]
      progress_callback = item.progress_callback
      if progress_callback:
        progress_callback(progress)
      
  def is_interrupted(self, task_id, raise_error = True):
    check.check_int(task_id)
    check.check_bool(raise_error)

    self._log.log_d(f'is_interrupted: task_id={task_id}')
    
    with self._lock as lock:
      if not task_id in self._tasks:
        if not raise_error:
          return False
        btask_error(f'No task_id "{task_id}" found to check for interruption')
      item = self._tasks[task_id]
      return item.interruped.value
      
  @classmethod
  def _function(clazz, task_id, function, add_time, debug, args):
    clazz._log.log_d(f'_function: task_id={task_id} function={function} args={args}')
    start_time = datetime.now()
    error = None
    data = None
    try:
      data = function(task_id, args)
      clazz._log.log_d(f'_function: task_id={task_id} data={data}')
      if not check.is_dict(data):
        raise btask_error(f'Function "{function}" should return a dict: "{data}" - {type(data)}')
    except Exception as ex:
      if debug:
        clazz._log.log_exception(ex)
      error = ex
    end_time = datetime.now()
    clazz._log.log_d(f'_function: task_id={task_id} data={data}')
    metadata = btask_result_metadata(btask_threading.current_process_pid(),
                                     add_time,
                                     start_time,
                                     end_time)
    result = btask_result(task_id, error == None, data, metadata, error, args)
    clazz._log.log_d(f'_function: result={result}')
    return result

  def _callback(self, result):
    check.check_btask_result(result)

    self._log.log_d(f'_callback: result={result} queue={self._queue}')
    self._queue.put(result)
    
  def _error_callback(self, error):
    self._log.log_exception(error)
    raise btask_error(f'unexpected error: "{error}"')
    
check.register_class(btask_pool, include_seq = False)

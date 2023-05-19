#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from datetime import datetime
import multiprocessing
import threading
import time

from bes.system.log import logger
from bes.system.check import check
from abc import abstractmethod, ABCMeta
from bes.system.compat import with_metaclass

from .btask_base import btask_base
from .btask_priority import btask_priority
from .btask_result import btask_result
from .btask_result_metadata import btask_result_metadata

class btask_result_collector_i(with_metaclass(ABCMeta, object)):

  _log = logger('btask')

  def __init__(self, queue):
    self._queue = queue
    self._thread = None

  @abstractmethod
  def handle_result(self, result):
    raise NotImplemented('handle_result')
    
  def _thread_main(self):
    while True:
      result = self._queue.get()
      if result == None:
        break
      self.handle_result(result)
    return 0
  
  def start(self):
    if self._thread:
      return
    self._thread = threading.Thread(target = self._thread_main, args = ())
    self._thread.start()

  def stop(self):
    if not self._thread:
      return
    self._queue.put(None)
    self._thread.join()
    self._thread = None
    
  _task_item = namedtuple('_task_item', 'task_id, callback')
  _tasks = {}
  _task_id = 1
  def add_task(self, category, priority, function, callback, *args, **kwargs):
    check.check_string(category)
    priority = check.check_btask_priority(priority)
    check.check_callable(function)
    check.check_callable(callback, allow_none = True)

    if multiprocessing.parent_process() != None:
      raise btask_error(f'Tasks can only be added from the main process')

    add_time = datetime.now()
    
    with self._lock as lock:
      task_id = self._task_id
      self._task_id += 1
      item = self._task_item(task_id, callback)
      self._tasks[task_id] = item

    task_args = tuple([ task_id, function, add_time ] + list(args))
    self._log.log_d(f'add_task: task_args={task_args}')
    self._pool.apply_async(self._function,
                           args = task_args,
                           kwds = kwargs,
                           callback = self._callback,
                           error_callback = self._error_callback)
    
  @classmethod
  def _function(clazz, task_id, function, add_time, *args, **kwargs):
    clazz._log.log_d(f'_function: task_id={task_id} function={function} args={args} kwargs={kwargs}')
    start_time = datetime.now()
    error = None
    data = None
    try:
      data = function(*args, **kwargs)
      if not check.is_dict(data):
        raise btask_error(f'Function "{function}" should return a dict: "{data}" - {type(data)}')
    except Exception as ex:
      clazz._log.log_exception(error)
      error = ex
    end_time = datetime.now()
    clazz._log.log_d(f'_function: task_id={task_id} data={data}')
    metadata = btask_result_metadata(multiprocessing.current_process().pid,
                                     add_time,
                                     start_time,
                                     end_time)
    result = btask_result(task_id, error == None, data, metadata, error)
    clazz._log.log_d(f'_function: result={result}')
    return result

  def _callback(self, result):
    check.check_btask_result(result)

    self._log.log_d(f'_callback: result={result} queue={self._queue}')
    self._queue.put(result)
    with self._lock as lock:
      del self._tasks[result.task_id]
    
  @classmethod
  def _error_callback(self, result):
    self._log.log_d(f'_error_callback: result={result}')
    assert False
    
check.register_class(btask_result_collector_i, name = 'btask_result_collector', include_seq = False)

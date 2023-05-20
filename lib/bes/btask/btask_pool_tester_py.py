#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import queue as py_queue

from bes.system.check import check
from bes.system.log import logger

from bes.btask.btask_main_thread_runner_py import btask_main_thread_runner_py
from bes.btask.btask_pool import btask_pool
from bes.btask.btask_result_collector_py import btask_result_collector_py

class btask_pool_tester_py(object):

  _log = logger('btask')
  
  def __init__(self, num_processes):
    check.check_int(num_processes)
    
    self._num_completed_tasks = 0
    self._num_added_tasks = 0

    self._runner = btask_main_thread_runner_py()
    self._pool = btask_pool(num_processes)
    self._collector = btask_result_collector_py(self._pool, self._runner)
    self._result_queue = py_queue.Queue()

  def start(self):
    self._collector.start()
    self._log.log_d(f'main: calling main_loop_start')
    self._runner.main_loop_start()
    self._log.log_d(f'main: main_loop_start returns')
    self._collector.stop()

  def stop(self):
    self._pool.close()
    
  def _after_callback(self):
    if self._num_completed_tasks == self._num_added_tasks:
      self._runner.main_loop_stop()

  def on_callback(self, result):
    self._result_queue.put(result)
    self._num_completed_tasks += 1
    self._after_callback()
      
  def add_task(self, function, callback = None, progress_callback = None, config = None, args = None):
    self._pool.add_task(function,
                        callback = callback,
                        progress_callback = progress_callback,
                        config = config,
                        args = args)
    self._num_added_tasks += 1

  def results(self):
    results = {}
    count = 0
    while True:
      result = self._result_queue.get()
      self._log.log_d(f'main: result={result}')
      count += 1
      assert result.task_id not in results
      results[result.task_id] = result
      if count == self._num_added_tasks:
        break
    return results

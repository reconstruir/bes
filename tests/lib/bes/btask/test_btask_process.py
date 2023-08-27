#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy
import time
from datetime import timedelta
from datetime import datetime
import threading
import multiprocessing

from bes.system.check import check
#from bes.system.execute import execute
from bes.system.execute_result import execute_result
from bes.system.log import logger
from bes.testing.unit_test import unit_test

from bes.btask.btask_cancelled_error import btask_cancelled_error
from bes.btask.btask_pool_tester_py import btask_pool_tester_py

from bes.btask.btask_process_data import btask_process_data
from bes.btask.btask_process import btask_process
from bes.btask.btask_task import btask_task
from bes.btask.btask_pool_item import btask_pool_item

class test_btask_process(unit_test):

  _log = logger('test')
  
  @classmethod
  def _function(clazz, context, args):
    clazz._log.log_d(f'_function: task_id={context.task_id} args={args}')
    result_error = args.get('__f_result_error', None)
    sleep_time_ms = args.get('__f_sleep_time_ms', None)
    if sleep_time_ms != None:
      sleep_time = (float(sleep_time_ms) / 1000.0) * 1.1
      time.sleep(sleep_time)
    if result_error:
      raise result_error
    result_data = args.get('__f_result_data', None)
    return result_data or {}

  @classmethod
  def _fix_args(clazz, args):
    result = {}
    for key, value in args.items():
      if not key.startswith('__f_'):
        result[key] = value
    return result

  @classmethod
  def _callback(clazz, result):
    clazz._log.log_d(f'_callback: result={result}')
  
  def test_process_one_process(self):
    self._log.log_d(f'test_process_one_process:')

    manager = multiprocessing.Manager()
    input_queue = manager.Queue()
    output_queue = manager.Queue()
    
    data = btask_process_data('kiwi1', input_queue, output_queue)
    process = btask_process(data)
    process.start()

    cancelled_value = manager.Value(bool, False)
    task = btask_pool_item(42,
                           datetime.now(),
                           ( 'kiwi', 'low', 2, self.DEBUG ),
                           self._function,
                           {
                             'number': 42,
                            'flavor': 'sweet',
                             '__f_result_data': { 'fruit': 'kiwi', 'color': 'green' },
                           },
                           self._callback,
                           None,
                           cancelled_value)
    input_queue.put(task)

    result = output_queue.get()
    input_queue.put(None)
    process.join()

  def test_process_many_processes(self):
    manager = multiprocessing.Manager()
    input_queue = manager.Queue()
    output_queue = manager.Queue()

    num_processes = 10
    num_tasks = 100
    
    processes = []
    for i in range(1, num_processes + 1):
      name = f'kiwi{i}'
      data = btask_process_data(name, input_queue, output_queue)
      process = btask_process(data)
      processes.append(process)
      process.start()

    for i in range(1, num_tasks + 1):
      cancelled_value = manager.Value(bool, False)
      task = btask_pool_item(42,
                             datetime.now(),
                             ( 'kiwi', 'low', 2, self.DEBUG ),
                             self._function,
                             {
                               'number': i,
                               'flavor': 'sweet',
                               '__f_result_data': { 'fruit': 'kiwi', 'color': 'green' },
                             },
                             self._callback,
                             None,
                             cancelled_value)
      input_queue.put(task)

    results = []
    for i in range(1, num_tasks + 1):
      result = output_queue.get()
      results.append(result)

    for i in range(1, num_processes + 1):
      input_queue.put(None)

    for process in processes:
      process.join()
    
if __name__ == '__main__':
  unit_test.main()

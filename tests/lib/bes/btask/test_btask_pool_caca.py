#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy
import time
import os
from datetime import timedelta
from datetime import datetime
import threading
import multiprocessing

from bes.system.check import check
from bes.system.execute_result import execute_result
from bes.system.log import logger
from bes.testing.unit_test import unit_test

from bes.btask.btask_cancelled_error import btask_cancelled_error
from bes.btask.btask_processor_tester_py import btask_processor_tester_py

from bes.btask.btask_process import btask_process
from bes.btask.btask_pool_item import btask_pool_item
from bes.btask.btask_pool_caca import btask_pool_caca

class test_btask_pool_caca(unit_test):

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
    result_data = args.get('__f_result_data', None) or {}
    result_data['pid'] = os.getpid()
    return result_data

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

    pc = btask_pool_caca(1)
    manager = multiprocessing.Manager()
#    input_queue = manager.Queue()
#    result_queue = manager.Queue()
    
#    data = btask_process_data('kiwi1', input_queue, result_queue)
#    process = btask_process(data)
#    process.start()

    add_time = datetime(year = 2022, month = 1, day = 1)
    start_time = datetime(year = 2022, month = 1, day = 2)
    end_time = datetime(year = 2022, month = 1, day = 3)

    cancelled_value = manager.Value(bool, False)
    task = btask_pool_item(42,
                           add_time,
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
    pc.start()
    pc.add_task(task)
    result = self._fix_result(pc.result_queue.get(), add_time, start_time, end_time)
    pc.stop()
    self.assert_json_equal(result.to_json(), '''{
  "task_id": 1, 
  "state": "SUCCESS", 
  "data": {
    "fruit": "kiwi", 
    "color": "green", 
    "pid": 1
  }, 
  "metadata": {
    "pid": 1, 
    "add_time": "2022-01-01 00:00:00", 
    "start_time": "2022-01-02 00:00:00", 
    "end_time": "2022-01-03 00:00:00"
  }, 
  "error": null, 
  "args": {
    "number": 42, 
    "flavor": "sweet", 
    "__f_result_data": {
      "fruit": "kiwi", 
      "color": "green", 
      "pid": 1
    }
  }
}
''')

  _fixed_task_ids = {}
  _fixed_pids = {}
  @classmethod
  def _fix_result(clazz, result, add_time, start_time, end_time):
    if result.task_id not in clazz._fixed_task_ids:
      clazz._fixed_task_ids[result.task_id] = len(clazz._fixed_task_ids) + 1
    if result.metadata.pid not in clazz._fixed_pids:
      clazz._fixed_pids[result.metadata.pid] = len(clazz._fixed_pids) + 1
    fixed_pid = clazz._fixed_pids[result.metadata.pid]
    fixed_metadata = result.metadata.clone(mutations = {
      'pid': fixed_pid,
      'add_time': add_time,
      'start_time': start_time,
      'end_time': end_time,
      })
    fixed_result = result.clone(mutations = {
      'task_id': clazz._fixed_task_ids[result.task_id],
      'metadata': fixed_metadata,
      })
    if '__f_result_data' in fixed_result.args:
      if 'pid' in fixed_result.args['__f_result_data']:
        fixed_result.args['__f_result_data']['pid'] = fixed_pid
    if fixed_result.data and 'pid' in fixed_result.data:
      fixed_result.data['pid'] = fixed_pid
    return fixed_result
    
  def xtest_process_many_processes(self):
    manager = multiprocessing.Manager()
    input_queue = manager.Queue()
    result_queue = manager.Queue()

    num_processes = 10
    num_tasks = 100
    
    processes = []
    for i in range(1, num_processes + 1):
      name = f'kiwi{i}'
      data = btask_process_data(name, input_queue, result_queue)
      process = btask_process(data)
      processes.append(process)
      process.start()

    for i in range(1, num_tasks + 1):
      cancelled_value = manager.Value(bool, False)
      task = btask_pool_item(42 + i,
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
      result = result_queue.get()
      results.append(result)

    for i in range(1, num_processes + 1):
      input_queue.put(None)

    for process in processes:
      process.join()

    for result in results:
      print(result.to_json())
      
if __name__ == '__main__':
  unit_test.main()

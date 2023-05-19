#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import queue as py_queue

from bes.system.check import check
from bes.system.execute import execute
from bes.system.log import logger

from bes.btask.btask_config import btask_config
from bes.btask.btask_main_thread_runner_py import btask_main_thread_runner_py
from bes.btask.btask_pool import btask_pool
from bes.btask.btask_result_collector_py import btask_result_collector_py


log = logger('demo')

class pool_tester(object):

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

class demo_handler(object):

  def __init__(self, tester):
    self._tester = tester
  
  @classmethod
  def _kiwi_function(clazz, args):
    log.log_d(f'_kiwi_function: args={args}')
    return {
      'fruit': 'kiwi',
      'color': 'green',
      'args': args,
    }

  def _kiwi_callback(self, result):
    log.log_d(f'_kiwi_callback: result={result}')
    self._tester.on_callback(result)

  @classmethod
  def _lemon_function(clazz, args):
    log.log_d(f'_lemon_function: args={args}')
    return {
      'fruit': 'lemon',
      'color': 'yellow',
      'args': args,
    }

  def _lemon_callback(self, result):
    log.log_d(f'_lemon_callback: result={result}')
    self._tester.on_callback(result)

  @classmethod
  def _grape_function(clazz, args):
    log.log_d(f'_grape_function: args={args}')
    raise RuntimeError(f'_grape_function failed')
    assert False

  def _grape_callback(self, result):
    log.log_d(f'_grape_callback: result={result}')
    self._tester.on_callback(result)

  @classmethod
  def _blackberry_function(clazz, args):
    log.log_d(f'_blackberry_function: args={args}')
    rv = execute.execute('true')
    return { 'rv': rv }

  def _blackberry_callback(self, result):
    log.log_d(f'_blackberry_callback: result={result}')
    self._tester.on_callback(result)

  @classmethod
  def _olive_function(clazz, args):
    log.log_d(f'_olive_function: args={args}')
    execute.execute('false')
    assert False

  def _olive_callback(self, result):
    log.log_d(f'_olive_callback: result={result}')
    self._tester.on_callback(result)
    
def main():
  log.log_d(f'main() starts')

  tester = pool_tester(8)
  handler = demo_handler(tester)

  debug = False
  kiwi_config = btask_config('kiwi', 'low', 2, debug)
  kiwi_id = tester.add_task(handler._kiwi_function,
                            callback = handler._kiwi_callback,
                            config = kiwi_config,
                            args = {
                              'number': 42,
                              'flavor': 'sweet',
                              }
                            )
  lemon_config = btask_config('lemon', 'low', 2, debug)
  lemon_id = tester.add_task(handler._lemon_function,
                             callback = handler._lemon_callback,
                             config = lemon_config,
                             args = {
                               'number': 666,
                               'flavor': 'tart',
                             })
  grape_id = tester.add_task(handler._grape_function,
                             callback = handler._grape_callback)
  blackberry_config = btask_config('blackberry', 'low', 2, debug)
  blackberry_id = tester.add_task(handler._blackberry_function,
                                  callback = handler._blackberry_callback,
                                  config = blackberry_config,
                                  args = {
                                    'number': 666,
                                    'flavor': 'tart',
                                  })
  olive_id = tester.add_task(handler._olive_function,
                             callback = handler._olive_callback)

  tester.start()

  results = tester.results()
  for task_id, result in results.items():
    print(f'main: task_id={task_id} pid={result.metadata.pid} data={result.data} error={result.error} - {type(result.error)}')
    
  return 0

if __name__ == '__main__':
  raise SystemExit(main())

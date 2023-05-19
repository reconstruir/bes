#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import queue as py_queue

from bes.btask.btask_processor import btask_processor
from bes.btask.btask_main_thread_runner_py import btask_main_thread_runner_py
from bes.btask.btask_result_collector_py import btask_result_collector_py
from bes.system.log import logger
from bes.system.execute import execute

log = logger('demo')

class tester(object):

  def __init__(self):
    self._count = 0
    self._num_tasks = 0

    self._runner = btask_main_thread_runner_py()
    self._processor = btask_processor(8)
    self._collector = btask_result_collector_py(self._processor, self._runner)
    self._result_queue = py_queue.Queue()

  def start(self):
    self._collector.start()
    log.log_d(f'main: calling main_loop_start')
    self._runner.main_loop_start()
    log.log_d(f'main: main_loop_start returns')
    self._collector.stop()

  def _after_callback(self):
    if self._count == self._num_tasks:
      self._runner.main_loop_stop()

  def on_callback(self, result):
    self._result_queue.put(result)
    self._count += 1
    self._after_callback()
      
  def add_task(self, category, priority, function, callback, debug, *args, **kwargs):
    self._processor.add_task(category, priority, function, callback, debug, *args, **kwargs)
    self._num_tasks += 1

  def results(self):
    results = {}
    count = 0
    while True:
      result = self._result_queue.get()
      log.log_d(f'main: result={result}')
      count += 1
      assert result.task_id not in results
      results[result.task_id] = result
      if count == self._num_tasks:
        break
    return results

class handler(object):

  def __init__(self, tester):
    self._tester = tester
  
  @classmethod
  def _kiwi_function(clazz, *args, **kwargs):
    log.log_d(f'_kiwi_function: args={args} kwargs={kwargs}')
    return {
      'fruit': 'kiwi',
      'color': 'green',
      'args': args,
      'kwargs': kwargs,
    }

  def _kiwi_callback(self, result):
    log.log_d(f'_kiwi_callback: result={result} count={self._tester._count}')
    self._tester.on_callback(result)

  @classmethod
  def _lemon_function(clazz, *args, **kwargs):
    log.log_d(f'_lemon_function: args={args} kwargs={kwargs}')
    return {
      'fruit': 'lemon',
      'color': 'yellow',
      'args': args,
      'kwargs': kwargs,
    }

  def _lemon_callback(self, result):
    log.log_d(f'_lemon_callback: result={result} count={self._tester._count}')
    self._tester.on_callback(result)

  @classmethod
  def _grape_function(clazz, *args, **kwargs):
    log.log_d(f'_grape_function: args={args} kwargs={kwargs}')
    raise RuntimeError(f'_grape_function failed')
    assert False

  def _grape_callback(self, result):
    log.log_d(f'_grape_callback: result={result} count={self._tester._count}')
    self._tester.on_callback(result)

  @classmethod
  def _blackberry_function(clazz, *args, **kwargs):
    log.log_d(f'_blackberry_function: args={args} kwargs={kwargs}')
    rv = execute.execute('true')
    return { 'rv': rv }

  def _blackberry_callback(self, result):
    log.log_d(f'_blackberry_callback: result={result} count={self._tester._count}')
    self._tester.on_callback(result)

  @classmethod
  def _olive_function(clazz, *args, **kwargs):
    log.log_d(f'_olive_function: args={args} kwargs={kwargs}')
    execute.execute('false')
    assert False

  def _olive_callback(self, result):
    log.log_d(f'_olive_callback: result={result} count={self._tester._count}')
    self._tester.on_callback(result)
    
def main():
  log.log_d(f'main() starts')

  t = tester()
  h = handler(t)

  debug = False
  kiwi_id = t.add_task('poto', 'low', h._kiwi_function, h._kiwi_callback, debug, 42, flavor = 'sweet')
  lemon_id = t.add_task('poto', 'low', h._lemon_function, h._lemon_callback, debug, 666, flavor = 'tart')
  grape_id = t.add_task('poto', 'low', h._grape_function, h._grape_callback, debug, 667, flavor = 'prune')
  blackberry_id = t.add_task('poto', 'low', h._blackberry_function, h._blackberry_callback, debug, 668, flavor = 'juicy')
  olive_id = t.add_task('poto', 'low', h._olive_function, h._olive_callback, debug, 669, flavor = 'black')

  t.start()

  results = t.results()
  for task_id, result in results.items():
    print(f'main: task_id={task_id} pid={result.metadata.pid} data={result.data} error={result.error} - {type(result.error)}')
    
  return 0

if __name__ == '__main__':
  raise SystemExit(main())

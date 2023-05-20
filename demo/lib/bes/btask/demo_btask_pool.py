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
from bes.btask.btask_pool_tester_py import btask_pool_tester_py

log = logger('demo')

class demo_handler(object):

  def __init__(self, tester):
    self._tester = tester
  
  @classmethod
  def _kiwi_function(clazz, task_id, args):
    log.log_d(f'_kiwi_function: task_id={task_id} args={args}')
    return {
      'fruit': 'kiwi',
      'color': 'green',
      'args': args,
    }

  def _kiwi_callback(self, result):
    log.log_d(f'_kiwi_callback: result={result}')
    self._tester.on_callback(result)

  @classmethod
  def _lemon_function(clazz, task_id, args):
    log.log_d(f'_lemon_function: task_id={task_id} args={args}')
    return {
      'fruit': 'lemon',
      'color': 'yellow',
      'args': args,
    }

  def _lemon_callback(self, result):
    log.log_d(f'_lemon_callback: result={result}')
    self._tester.on_callback(result)

  @classmethod
  def _grape_function(clazz, task_id, args):
    log.log_d(f'_grape_function: task_id={task_id} args={args}')
    raise RuntimeError(f'_grape_function failed')
    assert False

  def _grape_callback(self, result):
    log.log_d(f'_grape_callback: result={result}')
    self._tester.on_callback(result)

  @classmethod
  def _blackberry_function(clazz, task_id, args):
    log.log_d(f'_blackberry_function: task_id={task_id} args={args}')
    rv = execute.execute('true')
    return { 'rv': rv }

  def _blackberry_callback(self, result):
    log.log_d(f'_blackberry_callback: result={result}')
    self._tester.on_callback(result)

  @classmethod
  def _olive_function(clazz, task_id, args):
    log.log_d(f'_olive_function: task_id={task_id} args={args}')
    execute.execute('false')
    assert False

  def _olive_callback(self, result):
    log.log_d(f'_olive_callback: result={result}')
    self._tester.on_callback(result)
    
def main():
  log.log_d(f'main() starts')

  tester = btask_pool_tester_py(8)
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

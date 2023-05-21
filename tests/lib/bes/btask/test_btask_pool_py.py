#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy
import time
from datetime import timedelta

from bes.system.check import check
from bes.system.execute import execute
from bes.system.execute_result import execute_result
from bes.system.log import logger
from bes.testing.unit_test import unit_test

from bes.btask.btask_pool_tester_py import btask_pool_tester_py

log = logger('test')

class test_btask_pool_py(unit_test):

  _log = logger('test')
  
  @classmethod
  def _function(clazz, task_id, args):
    clazz._log.log_d(f'_function: task_id={task_id} args={args}')
    result_error = args.get('__f_result_error', None)
    sleep_time_ms = args.get('__f_sleet_time_ms', None)
    if sleep_time_ms != None:
      sleep_time = sleep_time_ms / 1000.0
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
  
  def test_add_task_with_8_processes(self):

    tester = btask_pool_tester_py(8)
  
    kiwi_id = tester.add_task(self._function,
                              callback = lambda r: tester.on_callback(r),
                              config = ('kiwi', 'low', 2, self.DEBUG),
                              args = {
                                'number': 42,
                                'flavor': 'sweet',
                                '__f_result_data': { 'fruit': 'kiwi', 'color': 'green' },
                              })
    lemon_id = tester.add_task(self._function,
                               callback = lambda r: tester.on_callback(r),
                               config = ('lemon', 'low', 2, self.DEBUG),
                               args = {
                                 'number': 666,
                                 'flavor': 'tart',
                                 '__f_result_data': { 'fruit': 'lemon', 'color': 'yellow' },
                               })
    grape_id = tester.add_task(self._function,
                               callback = lambda r: tester.on_callback(r),
                               args = {
                                 '__f_result_error': RuntimeError(f'_grape_function failed'),
                               })
  
    tester.start()
    results = tester.results()
    tester.stop()

    pids = [ r.metadata.pid for r in results.values() ]
    self.assertEqual( len(pids), len(set(pids)) )
    self.assertEqual( len(pids), tester._num_added_tasks )
    
    lemon_result = results[lemon_id]
    grape_result = results[grape_id]

    r = results[kiwi_id]
    self.assertEqual( kiwi_id, r.task_id )
    self.assertEqual( True, r.success )
    self.assertEqual( {
      'fruit': 'kiwi',
      'color': 'green',
    }, r.data )
    self.assertEqual( None, r.error )
    self.assertEqual( {
      'number': 42,
      'flavor': 'sweet',
    }, self._fix_args(r.args) )

    r = results[lemon_id]
    self.assertEqual( lemon_id, r.task_id )
    self.assertEqual( True, r.success )
    self.assertEqual( {
      'fruit': 'lemon',
      'color': 'yellow',
    }, r.data )
    self.assertEqual( None, r.error )
    self.assertEqual( {
      'number': 666,
      'flavor': 'tart',
    }, self._fix_args(r.args) )

    r = results[grape_id]
    self.assertEqual( grape_id, r.task_id )
    self.assertEqual( False, r.success )
    self.assertEqual( None, r.data )
    self.assertEqual( 'RuntimeError', r.error.__class__.__name__ )

  def test_add_task_with_1_process(self):
    tester = btask_pool_tester_py(1)
  
    kiwi_id = tester.add_task(self._function,
                              callback = lambda r: tester.on_callback(r),
                              args = { '__f_result_data': { 'fruit': 'kiwi', 'color': 'green' } })
    lemon_id = tester.add_task(self._function,
                              callback = lambda r: tester.on_callback(r),
                              args = { '__f_result_data': { 'fruit': 'lemon', 'color': 'yellow' } })
    grape_id = tester.add_task(self._function,
                               callback = lambda r: tester.on_callback(r),
                               args = {
                                 '__f_result_error': RuntimeError(f'_grape_function failed'),
                               })
  
    tester.start()
    results = tester.results()
    tester.stop()

    pids = [ r.metadata.pid for r in results.values() ]
    self.assertEqual( 1, len(set(pids)) )
    
    lemon_result = results[lemon_id]
    grape_result = results[grape_id]

    r = results[kiwi_id]
    self.assertEqual( kiwi_id, r.task_id )
    self.assertEqual( True, r.success )
    self.assertEqual( {
      'fruit': 'kiwi',
      'color': 'green',
    }, r.data )
    self.assertEqual( None, r.error )

    r = results[lemon_id]
    self.assertEqual( lemon_id, r.task_id )
    self.assertEqual( True, r.success )
    self.assertEqual( {
      'fruit': 'lemon',
      'color': 'yellow',
    }, r.data )
    self.assertEqual( None, r.error )

    r = results[grape_id]
    self.assertEqual( grape_id, r.task_id )
    self.assertEqual( False, r.success )
    self.assertEqual( None, r.data )
    self.assertEqual( 'RuntimeError', r.error.__class__.__name__ )

  def test_add_task_with_categories(self):

    tester = btask_pool_tester_py(8)

    sleep_time_ms = 250
    kiwi_ids = []
    kiwi_ids.append(tester.add_task(self._function,
                                    callback = lambda r: tester.on_callback(r),
                                    config = ( 'kiwi', 'low', 1, self.DEBUG ),
                                    args = {
                                      '__f_result_data': { 'num': 1, 'fruit': 'kiwi', 'color': 'green' },
                                      '__f_sleet_time_ms': sleep_time_ms,
                                    }))
    kiwi_ids.append(tester.add_task(self._function,
                                    callback = lambda r: tester.on_callback(r),
                                    config = ( 'kiwi', 'low', 1, self.DEBUG ),
                                    args = {
                                      '__f_result_data': { 'num': 2, 'fruit': 'kiwi', 'color': 'green' },
                                      '__f_sleet_time_ms': sleep_time_ms,
                                    }))
    kiwi_ids.append(tester.add_task(self._function,
                                    callback = lambda r: tester.on_callback(r),
                                    config = ( 'kiwi', 'low', 1, self.DEBUG ),
                                    args = {
                                      '__f_result_data': { 'num': 3, 'fruit': 'kiwi', 'color': 'green' },
                                      '__f_sleet_time_ms': sleep_time_ms,
                                    }))
    kiwi_ids.append(tester.add_task(self._function,
                                    callback = lambda r: tester.on_callback(r),
                                    config = ( 'kiwi', 'low', 1, self.DEBUG ),
                                    args = {
                                      '__f_result_data': { 'num': 4, 'fruit': 'kiwi', 'color': 'green' },
                                      '__f_sleet_time_ms': sleep_time_ms,
                                    }))

    tester.start()
    results = tester.results()
    tester.stop()

    self.assertEqual( True, results[1].metadata.duration >= timedelta(milliseconds = sleep_time_ms) )
    self.assertEqual( True, results[2].metadata.duration >= timedelta(milliseconds = sleep_time_ms) )
    self.assertEqual( True, results[3].metadata.duration >= timedelta(milliseconds = sleep_time_ms) )
    self.assertEqual( True, results[4].metadata.duration >= timedelta(milliseconds = sleep_time_ms) )

    self.assertEqual( True, results[1].metadata.total_duration >= timedelta(milliseconds = sleep_time_ms * 1) )
    self.assertEqual( True, results[2].metadata.total_duration >= timedelta(milliseconds = sleep_time_ms * 2) )
    self.assertEqual( True, results[3].metadata.total_duration >= timedelta(milliseconds = sleep_time_ms * 3) )
    self.assertEqual( True, results[4].metadata.total_duration >= timedelta(milliseconds = sleep_time_ms * 4) )

  def test_add_task_with_priority(self):

    tester = btask_pool_tester_py(8)

    sleep_time_ms = 250

    kiwi_ids = []
    kiwi_ids.append(tester.add_task(self._function,
                                    callback = lambda r: tester.on_callback(r),
                                    config = ( 'kiwi', 'low', 1, self.DEBUG ),
                                    args = {
                                      '__f_result_data': { 'num': 1, 'fruit': 'kiwi', 'color': 'green' },
                                      '__f_sleet_time_ms': sleep_time_ms,
                                    }))
    kiwi_ids.append(tester.add_task(self._function,
                                    callback = lambda r: tester.on_callback(r),
                                    config = ( 'kiwi', 'low', 1, self.DEBUG ),
                                    args = {
                                      '__f_result_data': { 'num': 2, 'fruit': 'kiwi', 'color': 'green' },
                                      '__f_sleet_time_ms': sleep_time_ms,
                                    }))
    kiwi_ids.append(tester.add_task(self._function,
                                    callback = lambda r: tester.on_callback(r),
                                    config = ( 'kiwi', 'low', 1, self.DEBUG ),
                                    args = {
                                      '__f_result_data': { 'num': 3, 'fruit': 'kiwi', 'color': 'green' },
                                      '__f_sleet_time_ms': sleep_time_ms,
                                    }))
    kiwi_ids.append(tester.add_task(self._function,
                                    callback = lambda r: tester.on_callback(r),
                                    config = ( 'kiwi', 'high', 1, self.DEBUG ),
                                    args = {
                                      '__f_result_data': { 'num': 4, 'fruit': 'kiwi', 'color': 'green' },
                                      '__f_sleet_time_ms': sleep_time_ms,
                                    }))

    tester.start()
    results = tester.results()
    tester.stop()

    self.assertEqual( True, results[1].metadata.duration >= timedelta(milliseconds = sleep_time_ms) )
    self.assertEqual( True, results[2].metadata.duration >= timedelta(milliseconds = sleep_time_ms) )
    self.assertEqual( True, results[3].metadata.duration >= timedelta(milliseconds = sleep_time_ms) )
    self.assertEqual( True, results[4].metadata.duration >= timedelta(milliseconds = sleep_time_ms) )

    self.assertEqual( True, results[1].metadata.total_duration >= timedelta(milliseconds = sleep_time_ms * 1) )
    self.assertEqual( True, results[2].metadata.total_duration >= timedelta(milliseconds = sleep_time_ms * 3) )
    self.assertEqual( True, results[3].metadata.total_duration >= timedelta(milliseconds = sleep_time_ms * 4) )
    self.assertEqual( True, results[4].metadata.total_duration >= timedelta(milliseconds = sleep_time_ms * 2) )
    
if __name__ == '__main__':
  unit_test.main()

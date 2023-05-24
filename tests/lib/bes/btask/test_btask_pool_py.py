#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy
import time
from datetime import timedelta
import threading

from bes.system.check import check
from bes.system.execute import execute
from bes.system.execute_result import execute_result
from bes.system.log import logger
from bes.testing.unit_test import unit_test

from bes.btask.btask_cancelled_error import btask_cancelled_error
from bes.btask.btask_pool_tester_py import btask_pool_tester_py
from bes.btask.btask_progress import btask_progress

class test_btask_pool_py(unit_test):

  _log = logger('test')
  
  @classmethod
  def _function(clazz, context, args):
    clazz._log.log_d(f'_function: task_id={context.task_id} args={args}')
    result_error = args.get('__f_result_error', None)
    sleep_time_ms = args.get('__f_sleet_time_ms', None)
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
    self.assertEqual( len(pids), tester._num_added_tasks )
    
    lemon_result = results[lemon_id]
    grape_result = results[grape_id]

    r = results[kiwi_id]
    self.assertEqual( kiwi_id, r.task_id )
    self.assertEqual( 'success', r.state )
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
    self.assertEqual( 'success', r.state )
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
    self.assertEqual( 'failed', r.state )
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
    self.assertEqual( 'success', r.state )
    self.assertEqual( {
      'fruit': 'kiwi',
      'color': 'green',
    }, r.data )
    self.assertEqual( None, r.error )

    r = results[lemon_id]
    self.assertEqual( lemon_id, r.task_id )
    self.assertEqual( 'success', r.state )
    self.assertEqual( {
      'fruit': 'lemon',
      'color': 'yellow',
    }, r.data )
    self.assertEqual( None, r.error )

    r = results[grape_id]
    self.assertEqual( grape_id, r.task_id )
    self.assertEqual( 'failed', r.state )
    self.assertEqual( None, r.data )
    self.assertEqual( 'RuntimeError', r.error.__class__.__name__ )

  def test_add_task_with_categories(self):

    tester = btask_pool_tester_py(8)

    sleep_time_ms = 250
    task_ids = []
    task_ids.append(tester.add_task(self._function,
                                    callback = lambda r: tester.on_callback(r),
                                    config = ( 'kiwi', 'low', 1, self.DEBUG ),
                                    args = {
                                      '__f_result_data': { 'num': 1, 'fruit': 'kiwi', 'color': 'green' },
                                      '__f_sleet_time_ms': sleep_time_ms,
                                    }))
    task_ids.append(tester.add_task(self._function,
                                    callback = lambda r: tester.on_callback(r),
                                    config = ( 'kiwi', 'low', 1, self.DEBUG ),
                                    args = {
                                      '__f_result_data': { 'num': 2, 'fruit': 'kiwi', 'color': 'green' },
                                      '__f_sleet_time_ms': sleep_time_ms,
                                    }))
    task_ids.append(tester.add_task(self._function,
                                    callback = lambda r: tester.on_callback(r),
                                    config = ( 'kiwi', 'low', 1, self.DEBUG ),
                                    args = {
                                      '__f_result_data': { 'num': 3, 'fruit': 'kiwi', 'color': 'green' },
                                      '__f_sleet_time_ms': sleep_time_ms,
                                    }))
    task_ids.append(tester.add_task(self._function,
                                    callback = lambda r: tester.on_callback(r),
                                    config = ( 'kiwi', 'low', 1, self.DEBUG ),
                                    args = {
                                      '__f_result_data': { 'num': 4, 'fruit': 'kiwi', 'color': 'green' },
                                      '__f_sleet_time_ms': sleep_time_ms,
                                    }))

    tester.start()
    results = tester.results()
    tester.stop()

    self.assertGreaterEqual( results[1].metadata.duration, timedelta(milliseconds = sleep_time_ms) )
    self.assertGreaterEqual( results[2].metadata.duration, timedelta(milliseconds = sleep_time_ms) )
    self.assertGreaterEqual( results[3].metadata.duration, timedelta(milliseconds = sleep_time_ms) )
    self.assertGreaterEqual( results[4].metadata.duration, timedelta(milliseconds = sleep_time_ms) )

    self.assertGreaterEqual( results[1].metadata.total_duration, timedelta(milliseconds = sleep_time_ms * 1) )
    self.assertGreaterEqual( results[2].metadata.total_duration, timedelta(milliseconds = sleep_time_ms * 2) )
    self.assertGreaterEqual( results[3].metadata.total_duration, timedelta(milliseconds = sleep_time_ms * 3) )
    self.assertGreaterEqual( results[4].metadata.total_duration, timedelta(milliseconds = sleep_time_ms * 4) )

  def test_add_task_with_priority(self):

    tester = btask_pool_tester_py(8)

    sleep_time_ms = 250

    task_ids = []
    task_ids.append(tester.add_task(self._function,
                                    callback = lambda r: tester.on_callback(r),
                                    config = ( 'kiwi', 'low', 1, self.DEBUG ),
                                    args = {
                                      '__f_result_data': { 'num': 1, 'fruit': 'kiwi', 'color': 'green' },
                                      '__f_sleet_time_ms': sleep_time_ms,
                                    }))
    task_ids.append(tester.add_task(self._function,
                                    callback = lambda r: tester.on_callback(r),
                                    config = ( 'kiwi', 'low', 1, self.DEBUG ),
                                    args = {
                                      '__f_result_data': { 'num': 2, 'fruit': 'kiwi', 'color': 'green' },
                                      '__f_sleet_time_ms': sleep_time_ms,
                                    }))
    task_ids.append(tester.add_task(self._function,
                                    callback = lambda r: tester.on_callback(r),
                                    config = ( 'kiwi', 'low', 1, self.DEBUG ),
                                    args = {
                                      '__f_result_data': { 'num': 3, 'fruit': 'kiwi', 'color': 'green' },
                                      '__f_sleet_time_ms': sleep_time_ms,
                                    }))
    task_ids.append(tester.add_task(self._function,
                                    callback = lambda r: tester.on_callback(r),
                                    config = ( 'kiwi', 'high', 1, self.DEBUG ),
                                    args = {
                                      '__f_result_data': { 'num': 4, 'fruit': 'kiwi', 'color': 'green' },
                                      '__f_sleet_time_ms': sleep_time_ms,
                                    }))

    tester.start()
    results = tester.results()
    tester.stop()

    self.assertGreaterEqual( results[1].metadata.duration, timedelta(milliseconds = sleep_time_ms) )
    self.assertGreaterEqual( results[2].metadata.duration, timedelta(milliseconds = sleep_time_ms) )
    self.assertGreaterEqual( results[3].metadata.duration, timedelta(milliseconds = sleep_time_ms) )
    self.assertGreaterEqual( results[4].metadata.duration, timedelta(milliseconds = sleep_time_ms) )

    self.assertGreaterEqual( results[1].metadata.total_duration, timedelta(milliseconds = sleep_time_ms * 1) )
    self.assertGreaterEqual( results[2].metadata.total_duration, timedelta(milliseconds = sleep_time_ms * 3) )
    self.assertGreaterEqual( results[3].metadata.total_duration, timedelta(milliseconds = sleep_time_ms * 4) )
    self.assertGreaterEqual( results[4].metadata.total_duration, timedelta(milliseconds = sleep_time_ms * 2) )

  @classmethod
  def _function_with_progress(clazz, context, args):
    clazz._log.log_d(f'_function_with_progress: task_id={context.task_id} args={args}')

    total = 5
    for i in range(1, total + 1):
      time.sleep(0.100)
      context.report_progress(i, total, f'doing stuff {i}')
    clazz._log.log_d(f'_function_with_progress: done')
    return {}
    
  def test_add_task_with_progress(self):
    tester = btask_pool_tester_py(1)

    pl = []
    def _progress_callback(progress):
      self._log.log_d(f'_progress_callback: progress={progress}')
      pl.append(progress)
      
    task_id = tester.add_task(self._function_with_progress,
                              callback = lambda r: tester.on_callback(r),
                              progress_callback = _progress_callback)
  
    tester.start()
    results = tester.results()
    tester.stop()

    r = results[task_id]
    self.assertEqual( task_id, r.task_id )
    self.assertEqual( 'success', r.state )
    self.assertEqual( {}, r.data )
    self.assertEqual( None, r.error )

    self.assertEqual( [
      ( 1, 1, 5, 'doing stuff 1' ),
      ( 1, 2, 5, 'doing stuff 2' ),
      ( 1, 3, 5, 'doing stuff 3' ),
      ( 1, 4, 5, 'doing stuff 4' ),
      ( 1, 5, 5, 'doing stuff 5' ),
    ], pl )

  def test_add_task_with_cancel_waiting(self):
    tester = btask_pool_tester_py(1)
      
    task_id1 = tester.add_task(self._function,
                               callback = lambda r: tester.on_callback(r),
                               config = ('kiwi', 'low', 1, self.DEBUG),
                               args = {
                                 '__f_result_data': { 'num': 1, 'fruit': 'kiwi' },
                                 '__f_sleet_time_ms': 500,
                               })
    task_id2 = tester.add_task(self._function,
                               callback = lambda r: tester.on_callback(r),
                               config = ('kiwi', 'low', 1, self.DEBUG),
                               args = {
                                 '__f_result_data': { 'num': 1, 'fruit': 'lemon' },
                                 '__f_sleet_time_ms': 0,
                               })
    
    def _cancel_thread_main():
      time.sleep(0.100)
      tester.pool.cancel(task_id2)
      return 0
    threading.Thread(target = _cancel_thread_main).start()
    
    tester.start()
    results = tester.results()
    tester.stop()

    self.assertEqual( 2, len(results) )
    
    r = results[task_id1]
    self.assertEqual( task_id1, r.task_id )
    self.assertEqual( 'success', r.state )
    self.assertEqual( { 'fruit': 'kiwi', 'num': 1 }, r.data )
    self.assertEqual( None, r.error )

    r = results[task_id2]
    self.assertEqual( task_id2, r.task_id )
    self.assertEqual( 'cancelled', r.state )
    self.assertEqual( None, r.error )
    
  @classmethod
  def _function_with_cancel(clazz, context, args):
    clazz._log.log_d(f'_function_with_cancel: task_id={context.task_id} args={args}')

    total = 10
    for i in range(1, total + 1):
      time.sleep(0.100)
      clazz._log.log_d(f'_function_with_cancel: i={i}')
      context.raise_cancelled_if_needed(f'cancelled')
    clazz._log.log_d(f'_function_with_cancel: done')
    return {}
    
  def test_add_task_with_cancel_in_progress(self):
    tester = btask_pool_tester_py(1)
      
    task_id1 = tester.add_task(self._function_with_cancel,
                               callback = lambda r: tester.on_callback(r),
                               config = ('kiwi', 'low', 1, self.DEBUG),
                               args = {
                                 '__f_result_data': { 'num': 1, 'fruit': 'kiwi' },
                                 '__f_sleet_time_ms': 500,
                               })
    
    task_id2 = tester.add_task(self._function,
                               callback = lambda r: tester.on_callback(r),
                               config = ('kiwi', 'low', 1, self.DEBUG),
                               args = {
                                 '__f_result_data': { 'num': 1, 'fruit': 'lemon' },
                                 '__f_sleet_time_ms': 0,
                               })

    def _cancel_thread_main():
      time.sleep(0.250)
      tester.pool.cancel(task_id1)
      return 0
    threading.Thread(target = _cancel_thread_main).start()
    
    tester.start()
    results = tester.results()
    tester.stop()

    self.assertEqual( 2, len(results) )
    
    self.assertEqual( True, task_id1 in results )
    self.assertEqual( True, task_id2 in results )
    
    r = results[task_id1]
    self.assertEqual( task_id1, r.task_id )
    self.assertEqual( 'cancelled', r.state )
    self.assertEqual( None, r.error )

    r = results[task_id2]
    self.assertEqual( task_id2, r.task_id )
    self.assertEqual( 'success', r.state )
    self.assertEqual( { 'num': 1, 'fruit': 'lemon' }, r.data )
    self.assertEqual( None, r.error )
    
if __name__ == '__main__':
  unit_test.main()

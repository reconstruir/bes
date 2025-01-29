#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import time
from datetime import timedelta
import threading

from bes.system.check import check
from bes.system.log import logger
from bes.testing.unit_test import unit_test

from bes.btask.btask_cancelled_error import btask_cancelled_error
from bes.btask.btask_processor_tester_py import btask_processor_tester_py
from bes.btask.btask_progress import btask_progress

class test_btask_processor_py(unit_test):

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
  
  def test_add_task_with_8_processes(self):

    tester = btask_processor_tester_py('test', 8)
  
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
    tester = btask_processor_tester_py('test', 1)
  
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

    tester = btask_processor_tester_py('test', 8)

    sleep_time_ms = 250
    task_ids = []
    task_ids.append(tester.add_task(self._function,
                                    callback = lambda r: tester.on_callback(r),
                                    config = ( 'kiwi', 'low', 1, self.DEBUG ),
                                    args = {
                                      '__f_result_data': { 'num': 1, 'fruit': 'kiwi', 'color': 'green' },
                                      '__f_sleep_time_ms': sleep_time_ms,
                                    }))
    task_ids.append(tester.add_task(self._function,
                                    callback = lambda r: tester.on_callback(r),
                                    config = ( 'kiwi', 'low', 1, self.DEBUG ),
                                    args = {
                                      '__f_result_data': { 'num': 2, 'fruit': 'kiwi', 'color': 'green' },
                                      '__f_sleep_time_ms': sleep_time_ms,
                                    }))
    task_ids.append(tester.add_task(self._function,
                                    callback = lambda r: tester.on_callback(r),
                                    config = ( 'kiwi', 'low', 1, self.DEBUG ),
                                    args = {
                                      '__f_result_data': { 'num': 3, 'fruit': 'kiwi', 'color': 'green' },
                                      '__f_sleep_time_ms': sleep_time_ms,
                                    }))
    task_ids.append(tester.add_task(self._function,
                                    callback = lambda r: tester.on_callback(r),
                                    config = ( 'kiwi', 'low', 1, self.DEBUG ),
                                    args = {
                                      '__f_result_data': { 'num': 4, 'fruit': 'kiwi', 'color': 'green' },
                                      '__f_sleep_time_ms': sleep_time_ms,
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

    tester = btask_processor_tester_py('test', 8)

    sleep_time_ms = 250

    task_ids = []
    task_ids.append(tester.add_task(self._function,
                                    callback = lambda r: tester.on_callback(r),
                                    config = ( 'kiwi', 'low', 1, self.DEBUG ),
                                    args = {
                                      '__f_result_data': { 'num': 1, 'fruit': 'kiwi', 'color': 'green' },
                                      '__f_sleep_time_ms': sleep_time_ms,
                                    }))
    task_ids.append(tester.add_task(self._function,
                                    callback = lambda r: tester.on_callback(r),
                                    config = ( 'kiwi', 'low', 1, self.DEBUG ),
                                    args = {
                                      '__f_result_data': { 'num': 2, 'fruit': 'kiwi', 'color': 'green' },
                                      '__f_sleep_time_ms': sleep_time_ms,
                                    }))
    task_ids.append(tester.add_task(self._function,
                                    callback = lambda r: tester.on_callback(r),
                                    config = ( 'kiwi', 'low', 1, self.DEBUG ),
                                    args = {
                                      '__f_result_data': { 'num': 3, 'fruit': 'kiwi', 'color': 'green' },
                                      '__f_sleep_time_ms': sleep_time_ms,
                                    }))
    task_ids.append(tester.add_task(self._function,
                                    callback = lambda r: tester.on_callback(r),
                                    config = ( 'kiwi', 'high', 1, self.DEBUG ),
                                    args = {
                                      '__f_result_data': { 'num': 4, 'fruit': 'kiwi', 'color': 'green' },
                                      '__f_sleep_time_ms': sleep_time_ms,
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
    sleep_time_before = args.get('sleep_time_before', 0.0)
    sleep_time_after = args.get('sleep_time_after', 0.0)
    minimum = args.get('minimum', 1)
    maximum = args.get('maximum', 5)

    clazz._log.log_d(f'_function_with_progress: task_id={context.task_id} args={args}')

    for value in range(minimum, maximum + 1):
      time.sleep(sleep_time_before)
      context.report_progress(minimum, maximum, value, f'doing stuff {value} of {maximum}')
      time.sleep(sleep_time_after)
    clazz._log.log_d(f'_function_with_progress: done')
    return {}
    
  def test_add_task_with_progress(self):
    tester = btask_processor_tester_py('test', 1)

    pl = []
    def _progress_callback(progress):
      self._log.log_d(f'_progress_callback: progress={progress}')
      pl.append(progress)
      time.sleep(0.250)
      
    task_id = tester.add_task(self._function_with_progress,
                              args = {
                                'sleep_time_before': 0.100,
                                'minimum': 1,
                                'maximum': 5,
                              },
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
      ( 1, 1, 5, 1, 'doing stuff 1 of 5' ),
      ( 1, 1, 5, 2, 'doing stuff 2 of 5' ),
      ( 1, 1, 5, 3, 'doing stuff 3 of 5' ),
      ( 1, 1, 5, 4, 'doing stuff 4 of 5' ),
      ( 1, 1, 5, 5, 'doing stuff 5 of 5' ),
    ], pl )

  def test_add_task_with_cancel_waiting(self):
    tester = btask_processor_tester_py('test', 1)
      
    task_id1 = tester.add_task(self._function,
                               callback = lambda r: tester.on_callback(r),
                               config = ('kiwi', 'low', 1, self.DEBUG),
                               args = {
                                 '__f_result_data': { 'num': 1, 'fruit': 'kiwi' },
                                 '__f_sleep_time_ms': 500,
                               })
    task_id2 = tester.add_task(self._function,
                               callback = lambda r: tester.on_callback(r),
                               config = ('kiwi', 'low', 1, self.DEBUG),
                               args = {
                                 '__f_result_data': { 'num': 1, 'fruit': 'lemon' },
                                 '__f_sleep_time_ms': 0,
                               })
    
    def _cancel_thread_main():
      time.sleep(0.100)
      tester.processor.cancel(task_id2)
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
    tester = btask_processor_tester_py('test', 1)
      
    task_id1 = tester.add_task(self._function_with_cancel,
                               callback = lambda r: tester.on_callback(r),
                               config = ('kiwi', 'low', 1, self.DEBUG),
                               args = {
                                 '__f_result_data': { 'num': 1, 'fruit': 'kiwi' },
                                 '__f_sleep_time_ms': 500,
                               })
    
    task_id2 = tester.add_task(self._function,
                               callback = lambda r: tester.on_callback(r),
                               config = ('kiwi', 'low', 1, self.DEBUG),
                               args = {
                                 '__f_result_data': { 'num': 1, 'fruit': 'lemon' },
                                 '__f_sleep_time_ms': 0,
                               })

    def _cancel_thread_main():
      time.sleep(0.250)
      tester.processor.cancel(task_id1)
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

  @classmethod
  def _function_many_tasks(clazz, context, args):
    clazz._log.log_d(f'_function_many_tasks: task_id={context.task_id} args={args}')
    sleep_time_ms = args.get('__f_sleep_time_ms', None)
    time.sleep(sleep_time_ms)
    return {}
  
    total = 10
    for i in range(1, total + 1):
      time.sleep(0.100)
      clazz._log.log_d(f'_function_with_cancel: i={i}')
      context.raise_cancelled_if_needed(f'cancelled')
    clazz._log.log_d(f'_function_with_cancel: done')
    return {}
    
  def test_add_and_cancel_many_tasks(self):
    tester = btask_processor_tester_py('test', 8)

    task_ids = []
    for i in range(0, 1000):
      task_id = tester.add_task(self._function_many_tasks,
                                callback = lambda r: tester.on_callback(r),
                                config = ('kiwi', 'low', 1, self.DEBUG),
                                args = {
                                  '__f_result_data': { 'num': i, 'fruit': 'kiwi' },
                                  '__f_sleep_time_ms': 10,
                                })
      task_ids.append(task_id)
    def _cancel_thread_main():
      time.sleep(0.250)
      for task_id in task_ids:
        tester.processor.cancel(task_id)
      return 0
    threading.Thread(target = _cancel_thread_main).start()
    
    tester.start()
    results = tester.results()
    tester.stop()

    self.assertEqual( len(task_ids), len(results) )

  def test_add_task_sync(self):
    tester = btask_processor_tester_py('test', 1)
    tester.start()
  
    r = tester.add_task_sync(self._function,
                             #callback = lambda r: tester.on_callback(r),
                             args = { '__f_result_data': { 'fruit': 'kiwi', 'color': 'green' } })
    print(f'r={r}')
#    results = tester.results()
    tester.stop()

    return
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
    
if __name__ == '__main__':
  unit_test.main()

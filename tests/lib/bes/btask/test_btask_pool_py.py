#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.system.execute import execute
from bes.system.execute_result import execute_result
from bes.system.log import logger
from bes.testing.unit_test import unit_test

from bes.btask.btask_config import btask_config
from bes.btask.btask_pool_tester_py import btask_pool_tester_py

log = logger('test')

class demo_handler(object):

  def __init__(self, tester):
    self._tester = tester
  
  @classmethod
  def _kiwi_function(clazz, task_id, args):
    log.log_d(f'_kiwi_function: task_id={task_id} args={args}')
    return {
      'fruit': 'kiwi',
      'color': 'green',
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

class test_btask_pool_py(unit_test):
  
  def test_basic(self):

    tester = btask_pool_tester_py(8)
    handler = demo_handler(tester)
  
    kiwi_config = btask_config('kiwi', 'low', 2, self.DEBUG)
    kiwi_id = tester.add_task(handler._kiwi_function,
                              callback = handler._kiwi_callback,
                              config = kiwi_config,
                              args = {
                                'number': 42,
                                'flavor': 'sweet',
                                }
                              )
    lemon_config = btask_config('lemon', 'low', 2, self.DEBUG)
    lemon_id = tester.add_task(handler._lemon_function,
                               callback = handler._lemon_callback,
                               config = lemon_config,
                               args = {
                                 'number': 666,
                                 'flavor': 'tart',
                               })
    grape_id = tester.add_task(handler._grape_function,
                               callback = handler._grape_callback)
    blackberry_config = btask_config('blackberry', 'low', 2, self.DEBUG)
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
    tester.stop()

    pids = [ r.metadata.pid for r in results.values() ]
    self.assertEqual( len(pids), len(set(pids)) )
    self.assertEqual( len(pids), tester._num_added_tasks )
    
    lemon_result = results[lemon_id]
    grape_result = results[grape_id]
    blackberry_result = results[blackberry_id]
    olive_result = results[olive_id]

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
    }, r.args )

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
    }, r.args )

    r = results[grape_id]
    self.assertEqual( grape_id, r.task_id )
    self.assertEqual( False, r.success )
    self.assertEqual( None, r.data )
    self.assertEqual( 'RuntimeError', r.error.__class__.__name__ )

    r = results[blackberry_id]
    self.assertEqual( blackberry_id, r.task_id )
    self.assertEqual( True, r.success )
    self.assertEqual( None, r.error )
    self.assertEqual( {
      'rv': execute_result(b'', b'', 0, [ 'true' ]),
    }, r.data )
    self.assertEqual( {
      'number': 666,
      'flavor': 'tart',
    }, r.args )

    r = results[olive_id]
    self.assertEqual( olive_id, r.task_id )
    self.assertEqual( False, r.success )
    self.assertEqual( None, r.data )
    self.assertEqual( 'RuntimeError', r.error.__class__.__name__ )

  def test_one_process(self):
    tester = btask_pool_tester_py(1)
    handler = demo_handler(tester)
  
    kiwi_id = tester.add_task(handler._kiwi_function,
                              callback = handler._kiwi_callback)
    lemon_id = tester.add_task(handler._lemon_function,
                               callback = handler._lemon_callback)
    grape_id = tester.add_task(handler._grape_function,
                               callback = handler._grape_callback)
    blackberry_id = tester.add_task(handler._blackberry_function,
                                    callback = handler._blackberry_callback)
    olive_id = tester.add_task(handler._olive_function,
                               callback = handler._olive_callback)
  
    tester.start()
    results = tester.results()
    tester.stop()

    pids = [ r.metadata.pid for r in results.values() ]
    self.assertEqual( 1, len(set(pids)) )
    
    lemon_result = results[lemon_id]
    grape_result = results[grape_id]
    blackberry_result = results[blackberry_id]
    olive_result = results[olive_id]

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

    r = results[blackberry_id]
    self.assertEqual( blackberry_id, r.task_id )
    self.assertEqual( True, r.success )
    self.assertEqual( None, r.error )
    self.assertEqual( {
      'rv': execute_result(b'', b'', 0, [ 'true' ]),
    }, r.data )

    r = results[olive_id]
    self.assertEqual( olive_id, r.task_id )
    self.assertEqual( False, r.success )
    self.assertEqual( None, r.data )
    self.assertEqual( 'RuntimeError', r.error.__class__.__name__ )
    
if __name__ == '__main__':
  unit_test.main()

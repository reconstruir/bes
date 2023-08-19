#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import multiprocessing
import time
import threading

import queue as py_queue

from bes.btask.btask_main_thread_runner_py import btask_main_thread_runner_py
from bes.system.log import logger

log = logger('demo')

def main():
  log.log_d(f'main() starts')
  
  runner = btask_main_thread_runner_py()
  
  def spawn(function, *args, **kwargs):
    def _spawn_main(*args, **kwargs):
      log.log_d(f'_spawn_main: args={args} kwargs={kwargs}')
      runner.call_in_main_thread(function, *args, **kwargs)
      return 0
    
    log.log_d(f'spawn: target={function} args={args} kwargs={kwargs}')
    t = threading.Thread(target = _spawn_main, args = ( function, ) + args, kwargs = kwargs)
    t.start()

  q = py_queue.Queue()

  def kiwi(*args, **kwargs):
    p = multiprocessing.parent_process()
    log.log_d(f'kiwi: p={p} args={args} kwargs={kwargs}')
    q.put( { 'name': 'kiwi', 'args': args, 'kwargs': kwargs } )

  def lemon(*args, **kwargs):
    p = multiprocessing.parent_process()
    log.log_d(f'lemon: p={p} args={args} kwargs={kwargs}')
    q.put( { 'name': 'lemon', 'args': args, 'kwargs': kwargs } )

  def stopper(*args, **kwargs):
    p = multiprocessing.parent_process()
    log.log_d(f'stopper: p={p} args={args} kwargs={kwargs}')
    time.sleep(5.0)
    runner.main_loop_stop()
    
  spawn(kiwi, 1, color = 'green')
  spawn(kiwi, 2, color = 'yellow')
  spawn(lemon, 1, color = 'green')
  spawn(lemon, 2, color = 'yellow')
  spawn(stopper)

  log.log_d(f'main: calling main_loop_start')
  runner.main_loop_start()
  log.log_d(f'main: main_loop_start returns')
    
  return 0

'''
class test_btask_main_thread_runner_py(unit_test):

  def test_call_in_main_thread(self):
    runner = btask_main_thread_runner()

    q = py_queue()
    
    def kiwi(*args, **kwargs):
      q.put( { 'name': 'kiwi', 'args': args, 'kwargs': kwargs } )

    def lemon(*args, **kwargs):
      q.put( { 'name': 'lemon', 'args': args, 'kwargs': kwargs } )

    def spawn(function, *args, **kwargs):
      def _thread_main(
      q.put( { 'name': 'lemon', 'args': args, 'kwargs': kwargs } )
      
      
    runner.call_in_main_thread(kiwi, 1, color = 'green')
    runner.call_in_main_thread(kiwi, 2, color = 'yellow')

    runner.call_in_main_thread(lemon, 1, color = 'green')
    runner.call_in_main_thread(lemon, 2, color = 'yellow')
'''

if __name__ == '__main__':
  multiprocessing.freeze_support()
  raise SystemExit(main())

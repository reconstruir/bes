#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import multiprocessing
import time
import threading

import queue as py_queue

from bes.btask.btask_processor import btask_processor
from bes.btask.btask_base import btask_base
from bes.btask.btask_main_thread_runner_py import btask_main_thread_runner_py
from bes.system.log import logger

log = logger('demo')

class kiwi_task(btask_base):

  def __init__(self, name, queue):
    super().__init__()

    self._name = name
    self._queue = queue
      
  #@abstractmethod
  def category(self):
    'Return category for this type of task'
    return f'kiwi-{self._name}'

  #@abstractmethod
  def priority(self):
    'Return  priority for this type of task'
    return 'low'

  @classmethod
  #@abstractmethod
  def run(clazz, *args, **kwargs):
    assert False
    print(f'kiwi_task.run(args={args} kwargs={kwargs}')
    return { 'name': 'x', 'pid': multiprocessing.current_process().pid }

  #@abstractmethod
  def callback(self, result):
    assert multiprocessing.parent_process() == None

    log.log_d(f'kiwi_task.callback: result={result}')

  def __getstate__(self):
    state = self.__dict__.copy()
    #del state['fun']
    return state
    
  def __setstate__(self, state):
    self.__dict__.update(state)  

class lemon_task(btask_base):

  def __init__(self, name, queue):
    super().__init__()
    self._name = name
    self._queue = queue
      
  #@abstractmethod
  def category(self):
    'Return category for this type of task'
    return f'lemon-{self._name}'

  #@abstractmethod
  def priority(self):
    'Return  priority for this type of task'
    return 'high'

  #@abstractmethod
  def run(self, *args, **kwargs):
    assert False
    print(f'kiwi_task.run(args={args} kwargs={kwargs}')
    return { 'name': self._name, 'pid': multiprocessing.current_process().pid }

  #@abstractmethod
  def callback(self, result):
    assert multiprocessing.parent_process() == None
      
    log.log_d(f'lemon_task.callback: result={result}')

def main():
  log.log_d(f'main() starts')
  
  runner = btask_main_thread_runner_py()

  queue = py_queue.Queue()
  
  processor = btask_processor(runner, 8)
      
  t1 = kiwi_task('foo', queue)
  t2 = kiwi_task('bar', queue)
  t3 = lemon_task('foo', queue)
  t4 = lemon_task('bar', queue)

  processor.add_task(t1, 1, color = 'purple')
#  processor.add_task(t2, 1, color = 'orange')
#  processor.add_task(t3, 1, color = 'green')
#  processor.add_task(t4, 1, color = 'yellow')
  
  def spawn(function, *args, **kwargs):
    def _spawn_main(*args, **kwargs):
      log.log_d(f'_spawn_main: args={args} kwargs={kwargs}')
      runner.call_in_main_thread(function, *args, **kwargs)
      return 0
    
    log.log_d(f'spawn: target={function} args={args} kwargs={kwargs}')
    t = threading.Thread(target = _spawn_main, args = ( function, ) + args, kwargs = kwargs)
    t.start()

#  q = py_queue.Queue()

#  def kiwi(*args, **kwargs):
#    p = multiprocessing.parent_process()
#    log.log_d(f'kiwi: p={p} args={args} kwargs={kwargs}')
#    q.put( { 'name': 'kiwi', 'args': args, 'kwargs': kwargs } )
#
#  def lemon(*args, **kwargs):
#    p = multiprocessing.parent_process()
#    log.log_d(f'lemon: p={p} args={args} kwargs={kwargs}')
#    q.put( { 'name': 'lemon', 'args': args, 'kwargs': kwargs } )

  def stopper(*args, **kwargs):
    p = multiprocessing.parent_process()
    log.log_d(f'stopper: p={p} args={args} kwargs={kwargs}')
    time.sleep(5.0)
    runner.main_loop_stop()
    
#  spawn(kiwi, 1, color = 'green')
#  spawn(kiwi, 2, color = 'yellow')
#  spawn(lemon, 1, color = 'green')
#  spawn(lemon, 2, color = 'yellow')
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

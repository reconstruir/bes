#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
import multiprocessing
import time

from bes.system.log import logger
from abc import abstractmethod, ABCMeta
from bes.system.compat import with_metaclass
from bes.system.check import check
from bes.enum_util.checked_int_enum import checked_int_enum

from .btask_base import btask_base

class btask_processor(object):

  _log = logger('btask')

  def __init__(self, runner, num_processes):
    check.check_btask_main_thread_runner(runner)
    check.check_int(num_processes)

    self._runner = runner
    self._pool = multiprocessing.Pool(num_processes)
#    self._pool.start()

    self.manager = multiprocessing.Manager()
    self.global_lock = self.manager.Lock()

  _task_item = namedtuple('_task_item', 'task_id, task, args, kwargs')
  _tasks = {}
  def add_task(self, task, *args, **kwargs):
    check.check_btask(task)

    if multiprocessing.parent_process() != None:
      raise btask_error(f'Tasks can only be added from the main process')
    
    task_id = id(task)

    if task_id in self._tasks:
      raise btask_error(f'Task already in process')

    task.manager = self.manager
    task.global_lock = self.global_lock
    
    item = self._task_item(task_id, task, args, kwargs)
    self._tasks[task_id] = item
    test_args = tuple([ task.__class__, task_id ] + list(args))
#    print(f'calling apply_sync args={test_args}')
    self._log.log_e(f'calling apply_sync args={test_args}')

    test_args = tuple([ task_id ] + list(args))
    
    def _callback(result):
      self._log.log_e(f'_callback: result={result}')
      print(f'_callback: result={result}', flush = True)

    def _error_callback(result):
      self._log.log_e(f'_error_callback: result={result}')
      print(f'_error_callback: result={result}', flush = True)

    #@abstractmethod
    def _target(*args, **kwargs):
      self._log.log_e(f'target: args={args} kwargs={kwargs}')
      assert False
      print(f'cacakiwi_task.run(args={args} kwargs={kwargs}')
      return { 'name': 'caca', 'pid': multiprocessing.current_process().pid }
    self._pool.apply_async(task.run, #self._function,
                           args = test_args,
                           kwds = kwargs,
                           callback = _callback,
                           error_callback = _error_callback)
    
  @classmethod
  def _function(clazz, *args, **kwargs):
    clazz._log.log_e(f'_function: args={args} kwargs={kwargs}')
    print(f'_function: args={args} kwargs={kwargs}', flush = True)
    return { 'name': 'caca', 'pid': multiprocessing.current_process().pid }
    
#  @classmethod
#  def _callback(clazz, result):
#    clazz._log.log_d(f'_callback: result={result}')

#  @classmethod
#  def _error_callback(clazz, result):
#    clazz._log.log_d(f'_error_callback: result={result}')
    
check.register_class(btask_processor, include_seq = False)
    
'''    
def main():
  pool = multiprocessing.Pool(8)

  t1 = task('red', 0)
  t2 = task('blue', 1)

  pool.apply_async(t1.run, ( 'caca', 666 ),
                   callback = t1._callback,
                   error_callback = t1._error_callback)

  pool.apply_async(t2.run, ( 'poto', 42 ),
                   callback = t2._callback,
                   error_callback = t2._error_callback)
  
  time.sleep(100)
  return 0
  
class task_foo(task_base):

  _log = logger('task_foo')
  
  def __init__(self, name, rv):
    super().__init__()
    
    self._name = name
    self._rv = rv
    self._log.log_d(f'id={id(self)}: {self._name} __init__')

  #@abstractmethod
  def category(self):
    'Return category for this type of task'
    return 'foo'

  #@abstractmethod
  def priority(self):
    'Return  priority for this type of task'
    return task_priority.LOW
    
  def run(self, *args, **kargs):
    self._log.log_d(f'id={id(self)}: {self._name} run: args={args} kargs={kargs}')
    return self._rv

  def _callback(self, result):
    self._log.log_d(f'id={id(self)}: {self._name} _callback: result={result}')

  def _error_callback(self, result):
    self._log.log_d(f'id={id(self)}: {self._name} _error_callback: result={result}')


def main():
  pool = multiprocessing.Pool(8)

  t1 = task('red', 0)
  t2 = task('blue', 1)

  pool.apply_async(t1.run, ( 'caca', 666 ),
                   callback = t1._callback,
                   error_callback = t1._error_callback)

  pool.apply_async(t2.run, ( 'poto', 42 ),
                   callback = t2._callback,
                   error_callback = t2._error_callback)
  
  time.sleep(100)
  return 0

if __name__ == '__main__':
  multiprocessing.freeze_support()
  raise SystemExit(main())
'''

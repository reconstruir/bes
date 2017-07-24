#!/usr/bin/env python
#-*- coding:utf-8 -*-

import atexit
from threading import Lock
from thread_pool import thread_pool
from decorators import synchronized_method #, synchronized_function
from bes.system import log

class global_thread_pool(object):
  'A global thread pool that can be used for misc tasks that dont require much oversight.'

  __num_threads = 8
  
  __pool = None
  __lock = Lock()

  @classmethod
  def set_num_threads(clazz, num_threads):
    success = False
    clazz.__lock.acquire()
    if not clazz.__pool:
      clazz.__num_threads = num_threads
      success = True
    clazz.__lock.release()
    if not success:
      raise RuntimeError('Global thread pool is already running.  Call set_num_threads() before add_task()')

  @classmethod
  def add_task(clazz, func, *args, **kargs):
    'Add a task to the global thread pool.'
    clazz.__lock.acquire()
    if not clazz.__pool:
      clazz.__pool = clazz.__start_global_thread_pool_i(clazz.__num_threads)
    clazz.__lock.release()
    clazz.__pool.add_task(func, *args, **kargs)
    
  @classmethod
  def __start_global_thread_pool_i(clazz, num_threads):
    clazz.log_d('Starting global thread pool with %d threads.' % (num_threads))
    gtp = thread_pool(num_threads = num_threads)

    def __global_thread_pool_atexit_cleanup(thread_pool):
      thread_pool.log_d('__global_thread_pool_atexit_cleanup(%s) waiting...' % (thread_pool))
      thread_pool.wait_completion()
      thread_pool.log_d('__global_thread_pool_atexit_cleanup(%s) done waiting...' % (thread_pool))

    atexit.register(__global_thread_pool_atexit_cleanup, gtp)
    return gtp

log.add_logging(global_thread_pool, 'global_thread_pool')

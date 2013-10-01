#!/usr/bin/env python
#-*- coding:utf-8 -*-

from Queue import Queue
from threading import Thread
from Log import Log
import atexit

# From http://code.activestate.com/recipes/577187-python-thread-pool/
class ThreadPoolWorker(Thread):
  """Thread executing tasks from a given tasks queue"""
  def __init__(self, tasks):
    Thread.__init__(self)
    self.tasks = tasks
    self.daemon = True
    self.start()
    self.log_d('Started worker %s for thread pool' % (self))
  
  def run(self):
    while True:
      func, args, kargs = self.tasks.get()
      self.log_d('Executing task %s(%s, %s)' % (func, str(args), str(kargs)))
      try:
        func(*args, **kargs)
      except Exception, ex:
        self.log_exception(ex)
      self.tasks.task_done()
      self.log_d('Done executing task %s' % (func))
Log.add_logging(ThreadPoolWorker, 'worker')

class ThreadPool(object):
  """Pool of threads consuming tasks from a queue"""

  global_thread_pool = None

  def __init__(self, num_threads):
    super(ThreadPool, self).__init__()
    self.log_d('Creating ThreadPool with %d threads.' % (num_threads))
    self.tasks = Queue(num_threads)
    for _ in range(num_threads):
      ThreadPoolWorker(self.tasks)

  def add_task(self, func, *args, **kargs):
    """Add a task to the queue"""
    self.log_d('add_task(%s)' % (func))
    self.tasks.put((func, args, kargs))

  def wait_completion(self):
    """Wait for completion of all the tasks in the queue"""
    self.log_d('wait_completion(%s) calling join' % (self))
    self.tasks.join()
    self.log_d('wait_completion(%s) join returns' % (self))

  @classmethod
  def get_global_thread_pool(clazz):
    assert clazz.global_thread_pool, 'Global thread pool has not been initialized.'
    return clazz.global_thread_pool

  @classmethod
  def start_global_thread_pool(clazz, num_threads = 4):
    assert not clazz.global_thread_pool, 'Global thread pool already initialized.'
    clazz.log_d('Starting global thread pool with %d threads.' % (num_threads))
    clazz.global_thread_pool = clazz(num_threads = num_threads)

    def cleanup(thread_pool):
      thread_pool.log_d('cleanup(%s) waiting...' % (thread_pool))
      thread_pool.wait_completion()
      thread_pool.log_d('cleanup(%s) done waiting...' % (thread_pool))

    atexit.register(cleanup, clazz.global_thread_pool)

Log.add_logging(ThreadPool, 'thread_pool')

if __name__ == '__main__':
  from random import randrange
  delays = [randrange(1, 10) for i in range(100)]
  
  from time import sleep
  def wait_delay(d):
    print 'sleeping for (%d)sec' % d
    sleep(d)
  
  # 1) Init a Thread pool with the desired number of threads
  pool = ThreadPool(20)
  
  for i, d in enumerate(delays):
    # print the percentage of tasks placed in the queue
    print '%.2f%c' % ((float(i)/float(len(delays)))*100.0,'%')
    
    # 2) Add the task to the queue
    pool.add_task(wait_delay, d)
  
  # 3) Wait for completion
  pool.wait_completion()

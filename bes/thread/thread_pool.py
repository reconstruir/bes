#!/usr/bin/env python
#-*- coding:utf-8 -*-

from Queue import Queue
from threading import Lock, Thread
from bes.system import log

# From http://code.activestate.com/recipes/577187-python-thread-pool/
class thread_pool_worker(Thread):
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
log.add_logging(thread_pool_worker, 'worker')

class thread_pool(object):
  """Pool of threads consuming tasks from a queue"""

  def __init__(self, num_threads):
    super(thread_pool, self).__init__()
    self.log_d('Creating thread_pool with %d threads.' % (num_threads))
    self.tasks = Queue(num_threads)
    for _ in range(num_threads):
      thread_pool_worker(self.tasks)

  def add_task(self, func, *args, **kargs):
    """Add a task to the queue"""
    self.log_d('add_task(%s)' % (func))
    self.tasks.put((func, args, kargs))

  def wait_completion(self):
    """Wait for completion of all the tasks in the queue"""
    self.log_d('wait_completion(%s) calling join' % (self))
    self.tasks.join()
    self.log_d('wait_completion(%s) join returns' % (self))

log.add_logging(thread_pool, 'thread_pool')

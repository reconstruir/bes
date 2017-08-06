#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import unittest
import random, time, threading
from bes.thread import global_thread_pool
import atexit

class test_global_thread_pool(unittest.TestCase):

  DEBUG = False
  #DEBUG = True
  
  def test_global_thread_pool(self):

    num_threads = 7
    num_tasks = 99
    
    self.count = 0
    self.count_lock = threading.Lock()
    
    def do_something(test_case, time_to_sleep):
      time.sleep(time_to_sleep)
      test_case.count_lock.acquire()
      test_case.count += 1
      if self.DEBUG:
        print('count: %d of %d' % (test_case.count, num_tasks))
      test_case.count_lock.release()

    for i in range(0, num_tasks):
      time_to_sleep = min(random.random() + 0.050, 0.100)
      global_thread_pool.add_task(do_something, self, time_to_sleep)

    def _check_count_at_exit(test_case, expected_count):
      test_case.count_lock.acquire()
      count = test_case.count
      test_case.count_lock.release()
      test_case.assertEqual( expected_count, count )

    # This doesnt work because atexit works in reverse order so theres no way to guarantee
    # this gets called after the global_thread_pool is done
    #atexit.register(_check_count_at_exit, self, num_tasks)
      
if __name__ == '__main__':
  unittest.main()

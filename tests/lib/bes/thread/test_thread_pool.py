#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import unittest
import random, time
from bes.thread.thread_pool import thread_pool

class test_thread_pool(unittest.TestCase):

  def test_thread_pool(self):

    def do_something(time_to_sleep):
      time.sleep(time_to_sleep)

    num_threads = 7
    num_tasks = 47
    pool = thread_pool(num_threads = num_threads)

    for i in range(0, num_threads * 10):
      time_to_sleep = min(random.random() + 0.050, 0.100)
      pool.add_task(do_something, time_to_sleep)

    pool.wait_completion()

if __name__ == "__main__":
  unittest.main()

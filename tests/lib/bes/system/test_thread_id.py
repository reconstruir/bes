#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

from bes.testing.unit_test import unit_test
from bes.system import thread_id

class test_thread_id(unit_test):

  def test_thread_id(self):
    self.assertTrue( thread_id.thread_id() not in [ 0, -1, None ] )
  
if __name__ == '__main__':
  unit_test.main()

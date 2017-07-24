#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

from bes.test import unit_test_helper
from bes.system import thread_id

class test_thread_id(unit_test_helper):

  def test_thread_id(self):
    self.assertTrue( thread_id.thread_id() not in [ 0, -1, None ] )
  
if __name__ == '__main__':
  unit_test_helper.main()

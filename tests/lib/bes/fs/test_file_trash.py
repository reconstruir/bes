#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.fs import file_trash, file_util, temp_file
from bes.system import log
import os.path as path
from collections import namedtuple
import time

log.configure('*=debug')

class test_file_trash(unit_test):

  _context = namedtuple('_context', 'trash_dir, stuff_dir, trash')
  
  def test_init(self):
    ctx = self._make_context()

  def test_start_stop(self):
    ctx = self._make_context(timeout = 0.500)
    ctx.trash.start()
    time.sleep(0.500)
    ctx.trash.stop()
    
  def test_start_no_stop(self):
    ctx = self._make_context(timeout = 0.100)
    ctx.trash.start()
    time.sleep(0.250)
    
  def _make_context(self, niceness_level = None, timeout = None, deleter = None):
    tmp_dir = temp_file.make_temp_dir()
    trash_dir = path.join(tmp_dir, 'trash')
    stuff_dir = path.join(tmp_dir, 'stuff')
    trash = file_trash(temp_file.make_temp_dir(),
                       niceness_level = niceness_level,
                       timeout = timeout,
                       deleter = deleter)
    return self._context(trash_dir, stuff_dir, trash)
    
if __name__ == '__main__':
  unit_test.main()

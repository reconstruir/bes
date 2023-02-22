#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
import time
import os.path as path

from bes.files.bfile_mtime_cached_info import bfile_mtime_cached_info
from bes.testing.unit_test import unit_test
  
class test_bfile_mtime_cached_info(unit_test):

  def test_value(self):
    tmp = self.make_temp_file(content = 'kiwi')
    a = bfile_mtime_cached_info(tmp, lambda f: path.getsize(f))
    self.assertEqual( 0, a.count )
    self.assertEqual( 4, a.value )
    self.assertEqual( 1, a.count )
    self.assertEqual( 4, a.value )
    self.assertEqual( 1, a.count )

  def test_value_changes(self):
    tmp = self.make_temp_file(content = 'kiwi')
    a = bfile_mtime_cached_info(tmp, lambda f: path.getsize(f))
    self.assertEqual( 0, a.count )
    self.assertEqual( 4, a.value )
    self.assertEqual( 1, a.count )
    self.assertEqual( 4, a.value )
    self.assertEqual( 1, a.count )
    old_mtime = path.getmtime(tmp)
    time.sleep(0.01)
    with open(tmp, 'w') as fout:
      fout.write('kiwikiwi')
      fout.flush()
#      os.fsync(fout.fileno())
#    filesystem.sync()
#    bfile_date.touch(tmp)
    new_mtime = path.getmtime(tmp)
    self.assertEqual( True, new_mtime != old_mtime )
    self.assertEqual( True, new_mtime > old_mtime )
    self.assertEqual( 8, a.value )
    self.assertEqual( 2, a.count )
    self.assertEqual( 8, a.value )
    self.assertEqual( 2, a.count )
    
if __name__ == '__main__':
  unit_test.main()

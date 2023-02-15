#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
import os.path as path

from bes.files.bfile_attr_memory_cached import bfile_attr_memory_cached
from bes.testing.unit_test import unit_test
from bes.system.filesystem import filesystem
  
class test_bfile_attr_memory_cached(unit_test):

  def test_value(self):
    tmp = self.make_temp_file(content = 'kiwi')
    a = bfile_attr_memory_cached(tmp, lambda f: path.getsize(f))
    self.assertEqual( 0, a.count )
    self.assertEqual( 4, a.value )
    self.assertEqual( 1, a.count )
    self.assertEqual( 4, a.value )
    self.assertEqual( 1, a.count )

  def test_value_changes(self):
    tmp = self.make_temp_file(content = 'kiwi')
    a = bfile_attr_memory_cached(tmp, lambda f: path.getsize(f))
    self.assertEqual( 0, a.count )
    self.assertEqual( 4, a.value )
    self.assertEqual( 1, a.count )
    self.assertEqual( 4, a.value )
    self.assertEqual( 1, a.count )
    with open(tmp, 'w') as fout:
      fout.write('kiwikiwi')
    filesystem.sync()
    self.assertEqual( 8, a.value )
    self.assertEqual( 2, a.count )
    self.assertEqual( 8, a.value )
    self.assertEqual( 2, a.count )
    
if __name__ == '__main__':
  unit_test.main()
    

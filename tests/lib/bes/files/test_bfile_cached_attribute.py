#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
import os.path as path

from bes.files.bfile_cached_attribute import bfile_cached_attribute
from bes.testing.unit_test import unit_test
from bes.system.filesystem import filesystem
  
class test_bfile_cached_attribute(unit_test):

  def test_foo(self):
    tmp = self.make_temp_file(content = 'kiwi')
    a = bfile_cached_attribute(tmp, lambda f: path.getsize(f))
    self.assertEqual( 0, a.count )
    self.assertEqual( 4, a.value )
    self.assertEqual( 1, a.count )
    self.assertEqual( 4, a.value )
    self.assertEqual( 1, a.count )
    
if __name__ == '__main__':
  unit_test.main()
    

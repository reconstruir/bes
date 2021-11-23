#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.testing.unit_test import unit_test
from bes.unix.brew.brew import brew
from bes.testing.unit_test_function_skip import unit_test_function_skip
from bes.testing.unit_test_class_skip import unit_test_class_skip

class test_brew(unit_test):
  '''
  brew unit tests.  Only runs if brew is installed.
  Mostly to go through the motions not much asserting is done
  '''
  
  @classmethod
  def setUpClass(clazz):
    unit_test_class_skip.raise_skip_if_not_unix()

  @unit_test_function_skip.skip_if(not brew.has_brew(), 'brew not installed')
  def test_available(self):
    for package_name in brew().available():
      self.assertTrue( bool(package_name) )

  @unit_test_function_skip.skip_if(not brew.has_brew(), 'brew not installed')
  def test_installed(self):
    for package_name in brew().installed():
      self.assertTrue( bool(package_name) )

  @unit_test_function_skip.skip_if(not brew.has_brew(), 'brew not installed')
  def test_files(self):
    b = brew()
    packages = b.installed()
    if not packages:
      return
    files = b.files(packages[0])
    for f in files:
      self.assertTrue( path.exists(f) )
      
if __name__ == '__main__':
  unit_test.main()

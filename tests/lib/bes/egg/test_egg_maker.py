#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.testing.egg_unit_test import egg_unit_test

class test_egg_unit_test(unit_test):

  def test_module_file_to_egg(self):
    self.assertEqual( self.xp_path('/foo/bar/baz/my.egg'),
                      egg_unit_test.module_file_to_egg(self.xp_path('/foo/bar/baz/my.egg/mymod/__init__.pyc')) )

  def test_module_file_to_egg_not_egg(self):
    self.assertEqual( None,
                      egg_unit_test.module_file_to_egg(self.xp_path('/foo/bar/baz/mymod/__init__.pyc')) )

if __name__ == '__main__':
  unit_test.main()

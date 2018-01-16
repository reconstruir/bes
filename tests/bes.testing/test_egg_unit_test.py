#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.testing.egg_unit_test import egg_unit_test

class test_egg_unit_test(unit_test):

  def test_module_file_to_egg(self):
    f = egg_unit_test.module_file_to_egg
    self.assertEqual( '/foo/bar/baz/my.egg', f('/foo/bar/baz/my.egg/mymod/__init__.pyc') )

  def test_module_file_to_egg_not_egg(self):
    f = egg_unit_test.module_file_to_egg
    self.assertEqual( None, f('/foo/bar/baz/mymod/__init__.pyc') )

if __name__ == '__main__':
  unit_test.main()

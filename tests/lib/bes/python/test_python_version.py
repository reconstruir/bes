#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.python.python_version import python_version

class test_python_version(unit_test):

  def test_version(self):
    self.assertEqual( '6.7', python_version.version('6.7.8') )

  def test_is_version(self):
    self.assertTrue( python_version.is_version('6.7') )
    self.assertFalse( python_version.is_version('6.7.8') )

  def test_is_full_version(self):
    self.assertTrue( python_version.is_full_version('6.7.8') )
    self.assertFalse( python_version.is_full_version('6.7') )

  def test_major_version(self):
    self.assertEqual( '6', python_version.major_version('6') )
    self.assertEqual( '6', python_version.major_version('6.7') )
    self.assertEqual( '6', python_version.major_version('6.7.8') )
    
if __name__ == '__main__':
  unit_test.main()

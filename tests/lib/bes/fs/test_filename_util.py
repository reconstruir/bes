#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from bes.fs.filename_util import filename_util

class test_filename_util(unit_test):

  def test_extension(self):
    self.assertEqual( None, filename_util.extension('a') )
    self.assertEqual( 'foo', filename_util.extension('a.foo') )
    self.assertEqual( 'gz', filename_util.extension('a.tar.gz') )

  def test_has_extension(self):
    self.assertTrue( filename_util.has_extension('a.foo', 'foo') )
    self.assertFalse( filename_util.has_extension('a.foo', 'png') )

  def test_has_any_extension(self):
    self.assertTrue( filename_util.has_any_extension('a.foo', ( 'foo', 'png' )) )
    self.assertFalse( filename_util.has_any_extension('a.foo', ( 'png', 'jpg' )) )

  def test_without_extension(self):
    self.assertEqual( 'a', filename_util.without_extension('a.foo') )
    self.assertEqual( 'a', filename_util.without_extension('a') )
    
if __name__ == '__main__':
  unit_test.main()

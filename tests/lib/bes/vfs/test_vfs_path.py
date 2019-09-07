#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test

from bes.vfs.vfs_path import vfs_path as P

class test_vfs_path(unit_test):

  def test_join(self):
    self.assertEqual( 'foo/bar', P.join('foo', 'bar') )
  
if __name__ == '__main__':
  unit_test.main()

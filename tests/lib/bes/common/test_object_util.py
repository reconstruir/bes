#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import unittest
from bes.common.object_util import object_util

class test_object_util(unittest.TestCase):

  def test_listify(self):
    self.assertEqual( [ 6 ], object_util.listify(6) )
    self.assertEqual( [ 6 ], object_util.listify([ 6 ]) )
    self.assertEqual( [ 'foo' ], object_util.listify('foo') )

  def test_is_homogeneous(self):
    self.assertTrue( object_util.is_homogeneous([ 1, 2, 3, 4 ], int) )
    self.assertFalse( object_util.is_homogeneous([ '1', 2, 3, 4 ], int ) )
    self.assertTrue( object_util.is_homogeneous([ '1', 2, 3, 4 ], ( int, str )) )
    self.assertFalse( object_util.is_homogeneous(False, bool) )

  def test_flatten_list_of_lists(self):
    self.assertTrue( [ 'a', 'b', 'c', 'd', 'e' ], object_util.flatten_list_of_lists( [ [ 'a', 'b' ], [ 'c' ], [ 'd', 'e' ] ] ) )

  def test_are_callable(self):
    self.assertTrue( object_util.are_callable([ lambda: 1 ]) )
    self.assertFalse( object_util.are_callable([ 1 ]) )
    self.assertTrue( object_util.are_callable(lambda: 1) )
    self.assertFalse( object_util.are_callable(1) )
    self.assertTrue( object_util.are_callable([ lambda: 1, lambda: 2 ]) )
    self.assertFalse( object_util.are_callable([ lambda: 1, 1 ]) )

if __name__ == '__main__':
  unittest.main()

#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import os, os.path as path, unittest
from bes.fs import file_path

class test_path(unittest.TestCase):

  def test_split(self):
    self.assertEqual( [ '', 'foo', 'bar' ], file_path.split('/foo/bar') )
    self.assertEqual( [ '', 'foo', 'bar' ], file_path.split('/foo/bar/') )
    self.assertEqual( [ '', 'foo', 'bar' ], file_path.split('/foo/bar//') )
    self.assertEqual( [ 'foo', 'bar' ], file_path.split('foo/bar') )

  def test_join(self):
    self.assertEqual( '/foo/bar', file_path.join([ '', 'foo', 'bar' ]) )
    self.assertEqual( '/foo/bar', file_path.join([ '', 'foo', 'bar' ]) )
    self.assertEqual( 'foo/bar', file_path.join([ 'foo', 'bar' ]) )

  def test_replace(self):
    self.assertEqual( '/foo/apple', file_path.replace('/foo/bar', 'bar', 'apple') )
    self.assertEqual( '/apple/apple', file_path.replace('/bar/bar', 'bar', 'apple') )
    self.assertEqual( '/apple/bar', file_path.replace('/bar/bar', 'bar', 'apple', count = 1) )
    self.assertEqual( '/bar/apple', file_path.replace('/bar/bar', 'bar', 'apple', count = 1, backwards = True) )

  def test_depth(self):
    self.assertEqual( 3, file_path.depth('/foo/bar') )
    self.assertEqual( 2, file_path.depth('/foo/') )
    self.assertEqual( 1, file_path.depth('/') )
    self.assertEqual( 0, file_path.depth('') )
    
if __name__ == "__main__":
  unittest.main()

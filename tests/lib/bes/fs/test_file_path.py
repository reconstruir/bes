#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import os, os.path as path, unittest
from bes.fs import file_path as FP

class test_path(unittest.TestCase):

  def test_split(self):
    self.assertEqual( [ '', 'foo', 'bar' ], FP.split('/foo/bar') )
    self.assertEqual( [ '', 'foo', 'bar' ], FP.split('/foo/bar/') )
    self.assertEqual( [ '', 'foo', 'bar' ], FP.split('/foo/bar//') )
    self.assertEqual( [ 'foo', 'bar' ], FP.split('foo/bar') )

  def test_join(self):
    self.assertEqual( '/foo/bar', FP.join([ '', 'foo', 'bar' ]) )
    self.assertEqual( '/foo/bar', FP.join([ '', 'foo', 'bar' ]) )
    self.assertEqual( 'foo/bar', FP.join([ 'foo', 'bar' ]) )

  def test_replace(self):
    self.assertEqual( '/foo/apple', FP.replace('/foo/bar', 'bar', 'apple') )
    self.assertEqual( '/apple/apple', FP.replace('/bar/bar', 'bar', 'apple') )
    self.assertEqual( '/apple/bar', FP.replace('/bar/bar', 'bar', 'apple', count = 1) )
    self.assertEqual( '/bar/apple', FP.replace('/bar/bar', 'bar', 'apple', count = 1, backwards = True) )

  def test_depth(self):
    self.assertEqual( 3, FP.depth('/foo/bar') )
    self.assertEqual( 2, FP.depth('/foo/') )
    self.assertEqual( 1, FP.depth('/') )
    self.assertEqual( 0, FP.depth('') )
    
  def test_parent_dir(self):
    self.assertEqual( '/foo', FP.parent_dir('/foo/bar/') )
    self.assertEqual( '/foo', FP.parent_dir('/foo/bar') )
    self.assertEqual( '/', FP.parent_dir('/foo') )
    self.assertEqual( None, FP.parent_dir('/') )

  def test_common_ancestor(self):
    self.assertEqual( 'base-1.2.3', FP.common_ancestor([
      'base-1.2.3/foo.txt',
      'base-1.2.3/bar.txt',
      'base-1.2.3/baz.txt',
    ]) )
    self.assertEqual( 'base-1.2.3', FP.common_ancestor([
      'base-1.2.3/foo.txt',
      'base-1.2.3/bar.txt',
      'base-1.2.3/here/baz.txt',
    ]) )
    self.assertEqual( 'base-1.2.3', FP.common_ancestor([
      'base-1.2.3/foo.txt',
      'base-1.2.3/bar.txt',
      'base-1.2.3',
    ]) )
    self.assertEqual( 'base-1.2.3', FP.common_ancestor([
      'base-1.2.3/foo.txt',
      'base-1.2.3/bar.txt',
      'base-1.2.3/',
    ]) )
    self.assertEqual( None, FP.common_ancestor([
      'base-1.2.3/foo.txt',
      'base-1.2.3/bar.txt',
      'base-1.2.4/baz.txt',
    ]) )

  def test_decompose(self):
    self.assertEqual( [ '/foo', '/foo/bar', '/foo/bar/baz' ], FP.decompose('/foo/bar/baz') )
    self.assertEqual( [ '/foo', '/foo/bar' ], FP.decompose('/foo/bar') )
    self.assertEqual( [ '/foo', ], FP.decompose('/foo') )
    self.assertEqual( [], FP.decompose('/') )
    
if __name__ == '__main__':
  unittest.main()

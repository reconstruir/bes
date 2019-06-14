#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, os.path as path, unittest

from bes.testing.unit_test import unit_test
from bes.fs.file_path import file_path as FP

class test_path(unit_test):

  def test_split(self):
    self.assertEqual( [ '', 'foo', 'bar' ], FP.split('/foo/bar') )
    self.assertEqual( [ '', 'foo', 'bar' ], FP.split('/foo/bar/') )
    self.assertEqual( [ '', 'foo', 'bar' ], FP.split('/foo/bar//') )
    self.assertEqual( [ 'foo', 'bar' ], FP.split('foo/bar') )

  def test_join(self):
    self.assertEqual( self.p('/foo/bar'), FP.join([ '', 'foo', 'bar' ]) )
    self.assertEqual( self.p('/foo/bar'), FP.join([ '', 'foo', 'bar' ]) )
    self.assertEqual( self.p('foo/bar'), FP.join([ 'foo', 'bar' ]) )

  def test_replace(self):
    self.assertEqual( self.p('/foo/apple'), FP.replace(self.p('/foo/bar'), 'bar', 'apple') )
    self.assertEqual( self.p('/apple/apple'), FP.replace(self.p('/bar/bar'), 'bar', 'apple') )
    self.assertEqual( self.p('/apple/bar'), FP.replace(self.p('/bar/bar'), 'bar', 'apple', count = 1) )
    self.assertEqual( self.p('/bar/apple'), FP.replace(self.p('/bar/bar'), 'bar', 'apple', count = 1, backwards = True) )

  def test_depth(self):
    self.assertEqual( 3, FP.depth('/foo/bar') )
    self.assertEqual( 2, FP.depth('/foo/') )
    self.assertEqual( 1, FP.depth('/') )
    self.assertEqual( 0, FP.depth('') )
    
  def test_parent_dir(self):
    self.assertEqual( self.p('/foo'), FP.parent_dir(self.p('/foo/bar/')) )
    self.assertEqual( self.p('/foo'), FP.parent_dir(self.p('/foo/bar')) )
    self.assertEqual( self.p('/'), FP.parent_dir(self.p('/foo')) )
    self.assertEqual( None, FP.parent_dir(self.p('/')) )

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
    self.assertEqual( [ self.p('/foo'), self.p('/foo/bar'), self.p('/foo/bar/baz') ], FP.decompose(self.p('/foo/bar/baz')) )
    self.assertEqual( [ self.p('/foo'), self.p('/foo/bar') ], FP.decompose(self.p('/foo/bar')) )
    self.assertEqual( [ self.p('/foo'), ], FP.decompose(self.p('/foo')) )
    self.assertEqual( [], FP.decompose(self.p('/')) )
    
if __name__ == "__main__":
  unit_test.main()

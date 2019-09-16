#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test

from bes.vfs.vfs_path import vfs_path as P

class test_vfs_path(unit_test):

  def test___str__(self):
    self.assertEqual( '/foo/bar', str(P('/foo/bar')) )
    self.assertEqual( '/foo/bar', str(P('/foo//bar')) )
    self.assertEqual( '/foo/bar/', str(P('/foo//bar/')) )
    self.assertEqual( '/foo/bar/', str(P('/foo/bar//')) )
    self.assertEqual( '/foo/bar', str(P('//foo/bar')) )
    self.assertEqual( '/foo/bar', str(P('///foo/bar')) )
    
  def test___add__(self):
    self.assertEqual( P('/foo/bar'), P('/foo') + P('bar') )
    self.assertEqual( P('/foo/bar'), P('/foo') + P('/bar') )
    self.assertEqual( P('/foo/bar/'), P('/foo') + P('/bar/') )
    self.assertEqual( P('/foo/bar'), P('foo') + P('bar') )
    
  def test_basename(self):
    self.assertEqual( 'bar', P('/foo/bar').basename )
    self.assertEqual( '', P('/foo/bar/').basename )
    
  def test_dirname(self):
    self.assertEqual( '/foo', P('/foo/bar').dirname )
    
  def test_parts(self):
    self.assertEqual( [ '', 'foo', 'bar' ], P('/foo/bar').parts )

  def test_path(self):
    self.assertEqual( '/foo/bar', P('/foo/bar').path )
    self.assertEqual( '/foo/bar', P('/foo//bar').path )
    self.assertEqual( '/foo/bar', P('foo/bar').path )
    self.assertEqual( '/foo/bar', P('foo//bar').path )
    
  def test_abs_path(self):
    self.assertEqual( '/foo/bar', P('/foo/bar').abs_path )
    self.assertEqual( '/foo/bar', P('/foo//bar').abs_path )
    self.assertEqual( '/foo/bar', P('foo/bar').abs_path )
    self.assertEqual( '/foo/bar', P('foo//bar').abs_path )

  def test_rel_path(self):
    self.assertEqual( 'foo/bar', P('/foo/bar').rel_path )
    self.assertEqual( 'foo/bar', P('/foo//bar').rel_path )
    self.assertEqual( 'foo/bar', P('foo/bar').rel_path )
    self.assertEqual( 'foo/bar', P('foo//bar').rel_path )
    
if __name__ == '__main__':
  unit_test.main()

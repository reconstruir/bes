#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test

from bes.vfs.vfs_path import vfs_path as P

class test_vfs_path(unit_test):

  def test_join(self):
    self.assertEqual( 'foo/bar', P.join('foo', 'bar') )

  def test_lstrip_sep(self):
    self.assertEqual( 'foo', P.lstrip_sep('foo') )
    self.assertEqual( 'foo', P.lstrip_sep('/foo') )
    self.assertEqual( 'foo/', P.lstrip_sep('/foo/') )
    self.assertEqual( '', P.lstrip_sep('/') )
    self.assertEqual( 'foo.txt', P.lstrip_sep('/foo.txt') )

  def test_rstrip_sep(self):
    self.assertEqual( 'foo', P.rstrip_sep('foo') )
    self.assertEqual( '/foo', P.rstrip_sep('/foo') )
    self.assertEqual( '/foo', P.rstrip_sep('/foo/') )
    self.assertEqual( '', P.rstrip_sep('/') )

  def test_strip_sep(self):
    self.assertEqual( 'foo', P.strip_sep('foo') )
    self.assertEqual( 'foo', P.strip_sep('/foo') )
    self.assertEqual( 'foo', P.strip_sep('/foo/') )
    self.assertEqual( '', P.strip_sep('/') )

  def test_ensure_rsep(self):
    self.assertEqual( 'bar/', P.ensure_rsep('bar') )
    self.assertEqual( 'bar/', P.ensure_rsep('bar/') )
    self.assertEqual( '/bar/', P.ensure_rsep('/bar/') )
    self.assertEqual( '/', P.ensure_rsep('') )
    self.assertEqual( '/', P.ensure_rsep('/') )
    self.assertEqual( 'foo/bar/', P.ensure_rsep('foo/bar') )
    self.assertEqual( '/foo/bar/', P.ensure_rsep('/foo/bar') )
    self.assertEqual( 'foo/bar/', P.ensure_rsep('foo/bar/') )
    self.assertEqual( '/foo/bar/', P.ensure_rsep('/foo/bar/') )

  def test_ensure_lsep(self):
    self.assertEqual( '/bar', P.ensure_lsep('bar') )
    self.assertEqual( '/bar/', P.ensure_lsep('bar/') )
    self.assertEqual( '/bar', P.ensure_lsep('/bar') )
    self.assertEqual( '/bar/', P.ensure_lsep('/bar/') )
    self.assertEqual( '/', P.ensure_lsep('') )
    self.assertEqual( '/', P.ensure_lsep('/') )
    self.assertEqual( '/foo/bar', P.ensure_lsep('foo/bar') )
    self.assertEqual( '/foo/bar/', P.ensure_lsep('foo/bar/') )
    
  def test_basename(self):
    self.assertEqual( '', P.basename('') )
    self.assertEqual( '', P.basename('/') )
    self.assertEqual( 'f', P.basename('/f') )
    self.assertEqual( 'b', P.basename('/f/b') )
    
  def test_dirname(self):
    self.assertEqual( '', P.dirname('') )
    self.assertEqual( '/', P.dirname('/') )
    self.assertEqual( '/', P.dirname('/f') )
    self.assertEqual( '/f', P.dirname('/f/b') )
    
if __name__ == '__main__':
  unit_test.main()

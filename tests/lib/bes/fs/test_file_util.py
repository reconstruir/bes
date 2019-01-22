#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

#log.configure('file_util=debug')

import unittest
import os, os.path as path, tempfile
from bes.fs import file_util

class test_file_util(unittest.TestCase):

  def test_lstrip_sep(self):
    self.assertEqual( 'foo', file_util.lstrip_sep('foo') )
    self.assertEqual( 'foo', file_util.lstrip_sep('/foo') )
    self.assertEqual( 'foo/', file_util.lstrip_sep('/foo/') )
    self.assertEqual( '', file_util.lstrip_sep('/') )

    self.assertEqual( 'foo', file_util.rstrip_sep('foo') )
    self.assertEqual( '/foo', file_util.rstrip_sep('/foo') )
    self.assertEqual( '/foo', file_util.rstrip_sep('/foo/') )
    self.assertEqual( '', file_util.rstrip_sep('/') )

    self.assertEqual( 'foo', file_util.strip_sep('foo') )
    self.assertEqual( 'foo', file_util.strip_sep('/foo') )
    self.assertEqual( 'foo', file_util.strip_sep('/foo/') )
    self.assertEqual( '', file_util.strip_sep('/') )

  def test_extension(self):
    self.assertEqual( 'zip', file_util.extension('foo.zip') )

  def test_remove_extension(self):
    self.assertEqual( 'foo', file_util.remove_extension('foo.zip') )
    self.assertEqual( '/foo/bar/kiwi', file_util.remove_extension('/foo/bar/kiwi.zip') )

  def test_ensure_rsep(self):
    self.assertEqual( 'bar/', file_util.ensure_rsep('bar') )
    self.assertEqual( 'bar/', file_util.ensure_rsep('bar/') )
    self.assertEqual( '/bar/', file_util.ensure_rsep('/bar/') )
    self.assertEqual( '/', file_util.ensure_rsep('') )
    self.assertEqual( '/', file_util.ensure_rsep('/') )
    self.assertEqual( 'foo/bar/', file_util.ensure_rsep('foo/bar') )
    self.assertEqual( '/foo/bar/', file_util.ensure_rsep('/foo/bar') )
    self.assertEqual( 'foo/bar/', file_util.ensure_rsep('foo/bar/') )
    self.assertEqual( '/foo/bar/', file_util.ensure_rsep('/foo/bar/') )

  def test_ensure_lsep(self):
    self.assertEqual( '/bar', file_util.ensure_lsep('bar') )
    self.assertEqual( '/bar/', file_util.ensure_lsep('bar/') )
    self.assertEqual( '/bar', file_util.ensure_lsep('/bar') )
    self.assertEqual( '/bar/', file_util.ensure_lsep('/bar/') )
    self.assertEqual( '/', file_util.ensure_lsep('') )
    self.assertEqual( '/', file_util.ensure_lsep('/') )
    self.assertEqual( '/foo/bar', file_util.ensure_lsep('foo/bar') )
    self.assertEqual( '/foo/bar/', file_util.ensure_lsep('foo/bar/') )

  def test_remove_head(self):
    self.assertEqual( 'bar', file_util.remove_head('foo/bar', 'foo') )
    self.assertEqual( 'bar/baz', file_util.remove_head('foo/bar/baz', 'foo') )
    self.assertEqual( 'foo', file_util.remove_head('foo', 'foo/') )
    self.assertEqual( 'foo', file_util.remove_head('foo', 'foo') )
    self.assertEqual( '', file_util.remove_head('foo/', 'foo/') )

  def test_remove_tail(self):
    self.assertEqual( '/foo', file_util.remove_tail('/foo/bar', 'bar') )
    self.assertEqual( 'foo', file_util.remove_tail('foo/bar', 'bar') )
    self.assertEqual( 'foo', file_util.remove_tail('foo/bar', '/bar') )
    
  def test_remove_head_unicode(self):
    self.assertEqual( u'bar', file_util.remove_head(u'foo/bar', u'foo') )

  def test_is_broken_link_true(self):
    tmp = tempfile.NamedTemporaryFile()
    file_util.remove(tmp.name)
    os.symlink('/somethingnotthere', tmp.name)
    self.assertEqual( True, path.islink(tmp.name) )
    self.assertEqual( True, file_util.is_broken_link(tmp.name) )

  def test_is_broken_link_false(self):
    tmp1 = tempfile.NamedTemporaryFile()
    tmp2 = tempfile.NamedTemporaryFile()
    file_util.remove(tmp1.name)
    os.symlink(tmp2.name, tmp1.name)
    self.assertEqual( True, path.islink(tmp1.name) )
    self.assertEqual( False, file_util.is_broken_link(tmp1.name) )

  def test_is_basename(self):
    self.assertEqual( True, file_util.is_basename('foo.txt') )
    self.assertEqual( False, file_util.is_basename('/foo.txt') )
    self.assertEqual( False, file_util.is_basename('a/foo.txt') )
    self.assertEqual( False, file_util.is_basename('a/b/c') )
    self.assertEqual( True, file_util.is_basename('') )

if __name__ == "__main__":
  unittest.main()

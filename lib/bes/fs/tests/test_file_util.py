#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

#log.configure('file_util=debug')

import unittest
from bes.fs import file_util

class Testfile_util(unittest.TestCase):

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

if __name__ == "__main__":
  unittest.main()

#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

# log.configure('file_util=debug')

import os, os.path as path, tempfile
from bes.testing.unit_test import unit_test
from bes.fs.file_util import file_util

class test_file_util(unit_test):

  def test_lstrip_sep(self):
    self.assertEqual( self.p('foo'), file_util.lstrip_sep('foo') )
    self.assertEqual( self.p('foo'), file_util.lstrip_sep(self.p('/foo')) )
    self.assertEqual( self.p('foo/'), file_util.lstrip_sep(self.p('/foo/')) )
    self.assertEqual( self.p(''), file_util.lstrip_sep(self.p('/')) )
    self.assertEqual( self.p('foo.txt'), file_util.lstrip_sep(self.p('/foo.txt')) )

  def test_rstrip_sep(self):
    self.assertEqual( self.p('foo'), file_util.rstrip_sep(self.p('foo')) )
    self.assertEqual( self.p('/foo'), file_util.rstrip_sep(self.p('/foo')) )
    self.assertEqual( self.p('/foo'), file_util.rstrip_sep(self.p('/foo/')) )
    self.assertEqual( self.p(''), file_util.rstrip_sep(self.p('/')) )

  def test_strip_sep(self):
    self.assertEqual( self.p('foo'), file_util.strip_sep(self.p('foo')) )
    self.assertEqual( self.p('foo'), file_util.strip_sep(self.p('/foo')) )
    self.assertEqual( self.p('foo'), file_util.strip_sep(self.p('/foo/')) )
    self.assertEqual( self.p(''), file_util.strip_sep(self.p('/')) )

  def test_extension(self):
    self.assertEqual( 'zip', file_util.extension('foo.zip') )

  def test_remove_extension(self):
    self.assertEqual( 'foo', file_util.remove_extension('foo.zip') )
    self.assertEqual( '/foo/bar/kiwi', file_util.remove_extension('/foo/bar/kiwi.zip') )

  def test_ensure_rsep(self):
    self.assertEqual( self.p('bar/'), file_util.ensure_rsep(self.p('bar')) )
    self.assertEqual( self.p('bar/'), file_util.ensure_rsep(self.p('bar/')) )
    self.assertEqual( self.p('/bar/'), file_util.ensure_rsep(self.p('/bar/')) )
    self.assertEqual( self.p('/'), file_util.ensure_rsep(self.p('')) )
    self.assertEqual( self.p('/'), file_util.ensure_rsep(self.p('/')) )
    self.assertEqual( self.p('foo/bar/'), file_util.ensure_rsep(self.p('foo/bar')) )
    self.assertEqual( self.p('/foo/bar/'), file_util.ensure_rsep(self.p('/foo/bar')) )
    self.assertEqual( self.p('foo/bar/'), file_util.ensure_rsep(self.p('foo/bar/')) )
    self.assertEqual( self.p('/foo/bar/'), file_util.ensure_rsep(self.p('/foo/bar/')) )

  def test_ensure_lsep(self):
    self.assertEqual( self.p('/bar'), file_util.ensure_lsep(self.p('bar')) )
    self.assertEqual( self.p('/bar/'), file_util.ensure_lsep(self.p('bar/')) )
    self.assertEqual( self.p('/bar'), file_util.ensure_lsep(self.p('/bar')) )
    self.assertEqual( self.p('/bar/'), file_util.ensure_lsep(self.p('/bar/')) )
    self.assertEqual( self.p('/'), file_util.ensure_lsep(self.p('')) )
    self.assertEqual( self.p('/'), file_util.ensure_lsep(self.p('/')) )
    self.assertEqual( self.p('/foo/bar'), file_util.ensure_lsep(self.p('foo/bar')) )
    self.assertEqual( self.p('/foo/bar/'), file_util.ensure_lsep(self.p('foo/bar/')) )

  def test_remove_head(self):
    self.assertEqual( self.p('bar'), file_util.remove_head(self.p('foo/bar'), self.p('foo')) )
    self.assertEqual( self.p('bar/baz'), file_util.remove_head(self.p('foo/bar/baz'), self.p('foo')) )
    self.assertEqual( self.p('foo'), file_util.remove_head(self.p('foo'), self.p('foo/')) )
    self.assertEqual( self.p('foo'), file_util.remove_head(self.p('foo'), self.p('foo')) )
    self.assertEqual( self.p(''), file_util.remove_head(self.p('foo/'), self.p('foo/')) )

  def test_remove_tail(self):
    self.assertEqual( self.p('/foo'), file_util.remove_tail(self.p('/foo/bar'), self.p('bar')) )
    self.assertEqual( self.p('foo'), file_util.remove_tail(self.p('foo/bar'), self.p('bar')) )
    self.assertEqual( self.p('foo'), file_util.remove_tail(self.p('foo/bar'), self.p('/bar')) )
    
  def test_remove_head_unicode(self):
    self.assertEqual( self.p(u'bar'), file_util.remove_head(self.p(u'foo/bar'), self.p(u'foo')) )

  def test_is_basename(self):
    self.assertEqual( True, file_util.is_basename('foo.txt') )
    self.assertEqual( False, file_util.is_basename('/foo.txt') )
    self.assertEqual( False, file_util.is_basename('a/foo.txt') )
    self.assertEqual( False, file_util.is_basename('a/b/c') )
    self.assertEqual( True, file_util.is_basename('') )

if __name__ == "__main__":
  unit_test.main()

#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

# log.configure('file_util=debug')

import os, os.path as path, tempfile
from datetime import datetime
from datetime import timedelta

from bes.testing.unit_test import unit_test
from bes.fs.file_util import file_util
from bes.common.hash_util import hash_util

class test_file_util(unit_test):

  def test_lstrip_sep(self):
    self.assertEqual( self.native_filename('foo'), file_util.lstrip_sep('foo') )
    self.assertEqual( self.native_filename('foo'), file_util.lstrip_sep(self.native_filename('/foo')) )
    self.assertEqual( self.native_filename('foo/'), file_util.lstrip_sep(self.native_filename('/foo/')) )
    self.assertEqual( self.native_filename(''), file_util.lstrip_sep(self.native_filename('/')) )
    self.assertEqual( self.native_filename('foo.txt'), file_util.lstrip_sep(self.native_filename('/foo.txt')) )

  def test_rstrip_sep(self):
    self.assertEqual( self.native_filename('foo'), file_util.rstrip_sep(self.native_filename('foo')) )
    self.assertEqual( self.native_filename('/foo'), file_util.rstrip_sep(self.native_filename('/foo')) )
    self.assertEqual( self.native_filename('/foo'), file_util.rstrip_sep(self.native_filename('/foo/')) )
    self.assertEqual( self.native_filename(''), file_util.rstrip_sep(self.native_filename('/')) )

  def test_strip_sep(self):
    self.assertEqual( self.native_filename('foo'), file_util.strip_sep(self.native_filename('foo')) )
    self.assertEqual( self.native_filename('foo'), file_util.strip_sep(self.native_filename('/foo')) )
    self.assertEqual( self.native_filename('foo'), file_util.strip_sep(self.native_filename('/foo/')) )
    self.assertEqual( self.native_filename(''), file_util.strip_sep(self.native_filename('/')) )

  def test_extension(self):
    self.assertEqual( 'zip', file_util.extension('foo.zip') )

  def test_remove_extension(self):
    self.assertEqual( 'foo', file_util.remove_extension('foo.zip') )
    self.assertEqual( '/foo/bar/kiwi', file_util.remove_extension('/foo/bar/kiwi.zip') )

  def test_ensure_rsep(self):
    self.assertEqual( self.native_filename('bar/'), file_util.ensure_rsep(self.native_filename('bar')) )
    self.assertEqual( self.native_filename('bar/'), file_util.ensure_rsep(self.native_filename('bar/')) )
    self.assertEqual( self.native_filename('/bar/'), file_util.ensure_rsep(self.native_filename('/bar/')) )
    self.assertEqual( self.native_filename('/'), file_util.ensure_rsep(self.native_filename('')) )
    self.assertEqual( self.native_filename('/'), file_util.ensure_rsep(self.native_filename('/')) )
    self.assertEqual( self.native_filename('foo/bar/'), file_util.ensure_rsep(self.native_filename('foo/bar')) )
    self.assertEqual( self.native_filename('/foo/bar/'), file_util.ensure_rsep(self.native_filename('/foo/bar')) )
    self.assertEqual( self.native_filename('foo/bar/'), file_util.ensure_rsep(self.native_filename('foo/bar/')) )
    self.assertEqual( self.native_filename('/foo/bar/'), file_util.ensure_rsep(self.native_filename('/foo/bar/')) )

  def test_ensure_lsep(self):
    self.assertEqual( self.native_filename('/bar'), file_util.ensure_lsep(self.native_filename('bar')) )
    self.assertEqual( self.native_filename('/bar/'), file_util.ensure_lsep(self.native_filename('bar/')) )
    self.assertEqual( self.native_filename('/bar'), file_util.ensure_lsep(self.native_filename('/bar')) )
    self.assertEqual( self.native_filename('/bar/'), file_util.ensure_lsep(self.native_filename('/bar/')) )
    self.assertEqual( self.native_filename('/'), file_util.ensure_lsep(self.native_filename('')) )
    self.assertEqual( self.native_filename('/'), file_util.ensure_lsep(self.native_filename('/')) )
    self.assertEqual( self.native_filename('/foo/bar'), file_util.ensure_lsep(self.native_filename('foo/bar')) )
    self.assertEqual( self.native_filename('/foo/bar/'), file_util.ensure_lsep(self.native_filename('foo/bar/')) )

  def test_remove_head(self):
    self.assertEqual( self.native_filename('bar'), file_util.remove_head(self.native_filename('foo/bar'), self.native_filename('foo')) )
    self.assertEqual( self.native_filename('bar/baz'), file_util.remove_head(self.native_filename('foo/bar/baz'), self.native_filename('foo')) )
    self.assertEqual( self.native_filename('foo'), file_util.remove_head(self.native_filename('foo'), self.native_filename('foo/')) )
    self.assertEqual( self.native_filename('foo'), file_util.remove_head(self.native_filename('foo'), self.native_filename('foo')) )
    self.assertEqual( self.native_filename(''), file_util.remove_head(self.native_filename('foo/'), self.native_filename('foo/')) )

  def test_remove_tail(self):
    self.assertEqual( self.native_filename('/foo'), file_util.remove_tail(self.native_filename('/foo/bar'), self.native_filename('bar')) )
    self.assertEqual( self.native_filename('foo'), file_util.remove_tail(self.native_filename('foo/bar'), self.native_filename('bar')) )
    self.assertEqual( self.native_filename('foo'), file_util.remove_tail(self.native_filename('foo/bar'), self.native_filename('/bar')) )
    
  def test_remove_head_unicode(self):
    self.assertEqual( self.native_filename(u'bar'), file_util.remove_head(self.native_filename(u'foo/bar'), self.native_filename(u'foo')) )

  def test_is_basename(self):
    self.assertEqual( True, file_util.is_basename('foo.txt') )
    self.assertEqual( False, file_util.is_basename('/foo.txt') )
    self.assertEqual( False, file_util.is_basename('a/foo.txt') )
    self.assertEqual( False, file_util.is_basename('a/b/c') )
    self.assertEqual( True, file_util.is_basename('') )

  def test_modification_date(self):
    yesterday = datetime.now() - timedelta(days = 1)
    tmp = self.make_temp_file()
    m1 = file_util.get_modification_date(tmp)
    file_util.set_modification_date(tmp, yesterday)
    self.assertEqual( yesterday, file_util.get_modification_date(tmp) )
    self.assertNotEqual( m1, file_util.get_modification_date(tmp) )

  def test_checksum_sha256(self):
    content = 'this is kiwi'
    tmp = self.make_temp_file()
    with open(tmp, 'wb') as f:
      f.write(content.encode('utf-8'))
      f.flush()
    actual = file_util.checksum('sha256', tmp)
    self.assertEqual( hash_util.hash_string_sha256(content), actual )

  def test_checksum_sha256_with_one_chunk(self):
    content = 'this is kiwi'
    tmp = self.make_temp_file()
    with open(tmp, 'wb') as f:
      f.write(content.encode('utf-8'))
      f.flush()
    actual = file_util.checksum('sha256', tmp, chunk_size = 4, num_chunks = 1)
    self.assertEqual( hash_util.hash_string_sha256('this'), actual )

  def test_checksum_sha256_with_two_chunks(self):
    content = 'this is kiwi'
    tmp = self.make_temp_file()
    with open(tmp, 'wb') as f:
      f.write(content.encode('utf-8'))
      f.flush()
    actual = file_util.checksum('sha256', tmp, chunk_size = 4, num_chunks = 2)
    self.assertEqual( hash_util.hash_string_sha256('this is '), actual )
    
if __name__ == '__main__':
  unit_test.main()

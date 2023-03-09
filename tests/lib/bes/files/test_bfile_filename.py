#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from bes.files.bfile_filename import bfile_filename

class test_bfile_filename(unit_test):

  def test_extension(self):
    self.assertEqual( None, bfile_filename.extension('a') )
    self.assertEqual( 'foo', bfile_filename.extension('a.foo') )
    self.assertEqual( 'gz', bfile_filename.extension('a.tar.gz') )
    self.assertEqual( 'png', bfile_filename.extension('.kiwi.png') )
    self.assertEqual( '', bfile_filename.extension('a.') )

  def test_has_extension(self):
    self.assertTrue( bfile_filename.has_extension('a.foo', 'foo') )
    self.assertFalse( bfile_filename.has_extension('a.foo', 'png') )

  def test_has_extension_with_ignore_case(self):
    self.assertTrue( bfile_filename.has_extension('a.foo', 'Foo', ignore_case = True) )
    self.assertFalse( bfile_filename.has_extension('a.foo', 'PNG', ignore_case = True) )
    self.assertFalse( bfile_filename.has_extension('a.foo', 'Foo', ignore_case = False) )
    
  def test_has_any_extension(self):
    self.assertTrue( bfile_filename.has_any_extension('a.foo', ( 'foo', 'png' )) )
    self.assertFalse( bfile_filename.has_any_extension('a.foo', ( 'png', 'jpg' )) )
    self.assertFalse( bfile_filename.has_any_extension('python3.7', ( 'exe', 'bat', 'cmd', 'ps1' )) )
    
  def test_has_any_extension_ignore_case(self):
    self.assertFalse( bfile_filename.has_any_extension('FOO.EXE', ( 'exe', 'bat' )) )
    self.assertTrue( bfile_filename.has_any_extension('FOO.EXE', ( 'exe', 'bat' ), ignore_case = True ) )
    self.assertFalse( bfile_filename.has_any_extension('python3.7', ( 'exe', 'bat', 'cmd', 'ps1' ), ignore_case = True) )
    
  def test_without_extension(self):
    self.assertEqual( 'a', bfile_filename.without_extension('a.foo') )
    self.assertEqual( 'a', bfile_filename.without_extension('a') )
    self.assertEqual( '.kiwi', bfile_filename.without_extension('.kiwi.png') )

  def test_split_extension(self):
    self.assertEqual( ( 'a', 'foo' ), bfile_filename.split_extension('a.foo') )
    self.assertEqual( ( 'a', None ), bfile_filename.split_extension('a') )
    self.assertEqual( ( '.kiwi', 'png' ), bfile_filename.split_extension('.kiwi.png') )
    self.assertEqual( ( 'a' , None ), bfile_filename.split_extension('a') )
    self.assertEqual( ( 'a', 'foo' ), bfile_filename.split_extension('a.foo') )
    self.assertEqual( ( 'a.tar', 'gz' ), bfile_filename.split_extension('a.tar.gz') )
    self.assertEqual( ( '.kiwi', 'png' ), bfile_filename.split_extension('.kiwi.png') )
    self.assertEqual( ( 'a', '' ), bfile_filename.split_extension('a.') )

  def test_prefix(self):
    self.assertEqual( None, bfile_filename.prefix('foo.txt') )
    self.assertEqual( None, bfile_filename.prefix('foo-.txt') )
    self.assertEqual( 'foo', bfile_filename.prefix('foo-42.txt') )
    self.assertEqual( None, bfile_filename.prefix('') )

  def test_add_extension(self):
    self.assertEqual( 'foo.txt', bfile_filename.add_extension('foo', 'txt') )
    self.assertEqual( 'foo', bfile_filename.add_extension('foo', '') )
    self.assertEqual( 'foo', bfile_filename.add_extension('foo', None) )
    self.assertEqual( '.txt', bfile_filename.add_extension('', 'txt') )

  def test_replace_extension(self):
    self.assertEqual( 'foo.txt', bfile_filename.replace_extension('foo.jpg', 'txt') )
    self.assertEqual( 'something.jpg.foo.txt', bfile_filename.replace_extension('something.jpg.foo.jpg', 'txt') )
    self.assertEqual( 'something', bfile_filename.replace_extension('something', 'txt') )
    self.assertEqual( '', bfile_filename.replace_extension('', 'txt') )
    self.assertEqual( 'foo.txt', bfile_filename.replace_extension('foo.txt', 'txt') )

  @classmethod
  def _test_shorten(clazz, filename, max_length, include_hash, hash_length):
    return bfile_filename.shorten(filename,
                             max_length = max_length,
                             include_hash = include_hash,
                             hash_length = hash_length)
    
  def test_shorten(self):
    self.assert_filename_equal( 'foo.jpg', self._test_shorten('foo.jpg', 8, False, None) )
    self.assert_filename_equal( 'foo.jpg', self._test_shorten('foo.jpg', 7, False, None) )
    self.assert_filename_equal( 'fo.jpg', self._test_shorten('foo.jpg', 6, False, None) )
    self.assert_filename_equal( 'f.jpg', self._test_shorten('foo.jpg', 5, False, None) )

  def test_shorten_no_extension(self):
    self.assert_filename_equal( 'foo', self._test_shorten('foo', 4, False, None) )
    self.assert_filename_equal( 'foo', self._test_shorten('foo', 3, False, None) )
    self.assert_filename_equal( 'fo', self._test_shorten('foo', 2, False, None) )
    self.assert_filename_equal( 'f', self._test_shorten('foo', 1, False, None) )
    
  def test_shorten_not_enough_space(self):
    with self.assertRaises(ValueError) as _:
      self._test_shorten('foo.jpg', 4, False, None)
    with self.assertRaises(ValueError) as _:
      self._test_shorten('foo.jpg', 3, False, None)

  def test_shorten_with_hash(self):
    self.assert_filename_equal( 'foo-e70422ca.jpg', self._test_shorten('foo12345678901234567890.jpg', 16, True, 8) )
    self.assert_filename_equal( 'fo-e70422ca.jpg', self._test_shorten('foo12345678901234567890.jpg', 15, True, 8) )
    self.assert_filename_equal( 'f-e70422ca.jpg', self._test_shorten('foo12345678901234567890.jpg', 14, True, 8) )
    self.assert_filename_equal( '-e70422ca.jpg', self._test_shorten('foo12345678901234567890.jpg', 13, True, 8) )

  def test_shorten_with_hash_not_enough_space(self):
    with self.assertRaises(ValueError) as _:
      self._test_shorten('foo12345678901234567890.jpg', 12, True, 8)

  def test_lstrip_sep(self):
    self.assertEqual( self.native_filename('foo'), bfile_filename.lstrip_sep('foo') )
    self.assertEqual( self.native_filename('foo'), bfile_filename.lstrip_sep(self.native_filename('/foo')) )
    self.assertEqual( self.native_filename('foo/'), bfile_filename.lstrip_sep(self.native_filename('/foo/')) )
    self.assertEqual( self.native_filename(''), bfile_filename.lstrip_sep(self.native_filename('/')) )
    self.assertEqual( self.native_filename('foo.txt'), bfile_filename.lstrip_sep(self.native_filename('/foo.txt')) )

  def test_rstrip_sep(self):
    self.assertEqual( self.native_filename('foo'), bfile_filename.rstrip_sep(self.native_filename('foo')) )
    self.assertEqual( self.native_filename('/foo'), bfile_filename.rstrip_sep(self.native_filename('/foo')) )
    self.assertEqual( self.native_filename('/foo'), bfile_filename.rstrip_sep(self.native_filename('/foo/')) )
    self.assertEqual( self.native_filename(''), bfile_filename.rstrip_sep(self.native_filename('/')) )

  def test_strip_sep(self):
    self.assertEqual( self.native_filename('foo'), bfile_filename.strip_sep(self.native_filename('foo')) )
    self.assertEqual( self.native_filename('foo'), bfile_filename.strip_sep(self.native_filename('/foo')) )
    self.assertEqual( self.native_filename('foo'), bfile_filename.strip_sep(self.native_filename('/foo/')) )
    self.assertEqual( self.native_filename(''), bfile_filename.strip_sep(self.native_filename('/')) )

  def test_ensure_rsep(self):
    self.assertEqual( self.native_filename('bar/'), bfile_filename.ensure_rsep(self.native_filename('bar')) )
    self.assertEqual( self.native_filename('bar/'), bfile_filename.ensure_rsep(self.native_filename('bar/')) )
    self.assertEqual( self.native_filename('/bar/'), bfile_filename.ensure_rsep(self.native_filename('/bar/')) )
    self.assertEqual( self.native_filename('/'), bfile_filename.ensure_rsep(self.native_filename('')) )
    self.assertEqual( self.native_filename('/'), bfile_filename.ensure_rsep(self.native_filename('/')) )
    self.assertEqual( self.native_filename('foo/bar/'), bfile_filename.ensure_rsep(self.native_filename('foo/bar')) )
    self.assertEqual( self.native_filename('/foo/bar/'), bfile_filename.ensure_rsep(self.native_filename('/foo/bar')) )
    self.assertEqual( self.native_filename('foo/bar/'), bfile_filename.ensure_rsep(self.native_filename('foo/bar/')) )
    self.assertEqual( self.native_filename('/foo/bar/'), bfile_filename.ensure_rsep(self.native_filename('/foo/bar/')) )

  def test_ensure_lsep(self):
    self.assertEqual( self.native_filename('/bar'), bfile_filename.ensure_lsep(self.native_filename('bar')) )
    self.assertEqual( self.native_filename('/bar/'), bfile_filename.ensure_lsep(self.native_filename('bar/')) )
    self.assertEqual( self.native_filename('/bar'), bfile_filename.ensure_lsep(self.native_filename('/bar')) )
    self.assertEqual( self.native_filename('/bar/'), bfile_filename.ensure_lsep(self.native_filename('/bar/')) )
    self.assertEqual( self.native_filename('/'), bfile_filename.ensure_lsep(self.native_filename('')) )
    self.assertEqual( self.native_filename('/'), bfile_filename.ensure_lsep(self.native_filename('/')) )
    self.assertEqual( self.native_filename('/foo/bar'), bfile_filename.ensure_lsep(self.native_filename('foo/bar')) )
    self.assertEqual( self.native_filename('/foo/bar/'), bfile_filename.ensure_lsep(self.native_filename('foo/bar/')) )

  def test_remove_head(self):
    self.assertEqual( self.native_filename('bar'), bfile_filename.remove_head(self.native_filename('foo/bar'), self.native_filename('foo')) )
    self.assertEqual( self.native_filename('bar/baz'), bfile_filename.remove_head(self.native_filename('foo/bar/baz'), self.native_filename('foo')) )
    self.assertEqual( self.native_filename('foo'), bfile_filename.remove_head(self.native_filename('foo'), self.native_filename('foo/')) )
    self.assertEqual( self.native_filename('foo'), bfile_filename.remove_head(self.native_filename('foo'), self.native_filename('foo')) )
    self.assertEqual( self.native_filename(''), bfile_filename.remove_head(self.native_filename('foo/'), self.native_filename('foo/')) )

  def test_remove_tail(self):
    self.assertEqual( self.native_filename('/foo'), bfile_filename.remove_tail(self.native_filename('/foo/bar'), self.native_filename('bar')) )
    self.assertEqual( self.native_filename('foo'), bfile_filename.remove_tail(self.native_filename('foo/bar'), self.native_filename('bar')) )
    self.assertEqual( self.native_filename('foo'), bfile_filename.remove_tail(self.native_filename('foo/bar'), self.native_filename('/bar')) )
    
    
if __name__ == '__main__':
  unit_test.main()

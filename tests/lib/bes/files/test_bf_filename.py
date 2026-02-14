#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from bes.files.bf_filename import bf_filename

class test_bf_filename(unit_test):

  def test_extension(self):
    self.assertEqual( None, bf_filename.extension('a') )
    self.assertEqual( 'foo', bf_filename.extension('a.foo') )
    self.assertEqual( 'gz', bf_filename.extension('a.tar.gz') )
    self.assertEqual( 'png', bf_filename.extension('.kiwi.png') )
    self.assertEqual( '', bf_filename.extension('a.') )

  def test_has_extension(self):
    self.assertTrue( bf_filename.has_extension('a.foo', 'foo') )
    self.assertFalse( bf_filename.has_extension('a.foo', 'png') )

  def test_has_extension_with_ignore_case(self):
    self.assertTrue( bf_filename.has_extension('a.foo', 'Foo', ignore_case = True) )
    self.assertFalse( bf_filename.has_extension('a.foo', 'PNG', ignore_case = True) )
    self.assertFalse( bf_filename.has_extension('a.foo', 'Foo', ignore_case = False) )
    
  def test_has_any_extension(self):
    self.assertTrue( bf_filename.has_any_extension('a.foo', ( 'foo', 'png' )) )
    self.assertFalse( bf_filename.has_any_extension('a.foo', ( 'png', 'jpg' )) )
    self.assertFalse( bf_filename.has_any_extension('python3.7', ( 'exe', 'bat', 'cmd', 'ps1' )) )
    
  def test_has_any_extension_ignore_case(self):
    self.assertFalse( bf_filename.has_any_extension('FOO.EXE', ( 'exe', 'bat' )) )
    self.assertTrue( bf_filename.has_any_extension('FOO.EXE', ( 'exe', 'bat' ), ignore_case = True ) )
    self.assertFalse( bf_filename.has_any_extension('python3.7', ( 'exe', 'bat', 'cmd', 'ps1' ), ignore_case = True) )
    
  def test_without_extension(self):
    self.assertEqual( 'a', bf_filename.without_extension('a.foo') )
    self.assertEqual( 'a', bf_filename.without_extension('a') )
    self.assertEqual( '.kiwi', bf_filename.without_extension('.kiwi.png') )

  def test_split_extension(self):
    self.assertEqual( ( 'a', 'foo' ), bf_filename.split_extension('a.foo') )
    self.assertEqual( ( 'a', None ), bf_filename.split_extension('a') )
    self.assertEqual( ( '.kiwi', 'png' ), bf_filename.split_extension('.kiwi.png') )
    self.assertEqual( ( 'a' , None ), bf_filename.split_extension('a') )
    self.assertEqual( ( 'a', 'foo' ), bf_filename.split_extension('a.foo') )
    self.assertEqual( ( 'a.tar', 'gz' ), bf_filename.split_extension('a.tar.gz') )
    self.assertEqual( ( '.kiwi', 'png' ), bf_filename.split_extension('.kiwi.png') )
    self.assertEqual( ( 'a', '' ), bf_filename.split_extension('a.') )

  def test_prefix(self):
    self.assertEqual( None, bf_filename.prefix('foo.txt') )
    self.assertEqual( None, bf_filename.prefix('foo-.txt') )
    self.assertEqual( 'foo', bf_filename.prefix('foo-42.txt') )
    self.assertEqual( None, bf_filename.prefix('') )

  def test_add_extension(self):
    self.assertEqual( 'foo.txt', bf_filename.add_extension('foo', 'txt') )
    self.assertEqual( 'foo', bf_filename.add_extension('foo', '') )
    self.assertEqual( 'foo', bf_filename.add_extension('foo', None) )
    self.assertEqual( '.txt', bf_filename.add_extension('', 'txt') )

  def test_replace_extension(self):
    self.assertEqual( 'foo.txt', bf_filename.replace_extension('foo.jpg', 'txt') )
    self.assertEqual( 'something.jpg.foo.txt', bf_filename.replace_extension('something.jpg.foo.jpg', 'txt') )
    self.assertEqual( 'something', bf_filename.replace_extension('something', 'txt') )
    self.assertEqual( '', bf_filename.replace_extension('', 'txt') )
    self.assertEqual( 'foo.txt', bf_filename.replace_extension('foo.txt', 'txt') )

  @classmethod
  def _test_shorten(clazz, filename, max_length, include_hash, hash_length):
    return bf_filename.shorten(filename,
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

  @classmethod
  def _test_shorten_bytes(clazz, filename, max_length_bytes, include_hash, hash_length):
    return bf_filename.shorten_bytes(filename,
                                     max_length_bytes = max_length_bytes,
                                     include_hash = include_hash,
                                     hash_length = hash_length)

  def test_shorten_bytes(self):
    self.assert_filename_equal( 'foo.jpg', self._test_shorten_bytes('foo.jpg', 8, False, None) )
    self.assert_filename_equal( 'foo.jpg', self._test_shorten_bytes('foo.jpg', 7, False, None) )
    self.assert_filename_equal( 'fo.jpg', self._test_shorten_bytes('foo.jpg', 6, False, None) )
    self.assert_filename_equal( 'f.jpg', self._test_shorten_bytes('foo.jpg', 5, False, None) )

  def test_shorten_bytes_no_extension(self):
    self.assert_filename_equal( 'foo', self._test_shorten_bytes('foo', 4, False, None) )
    self.assert_filename_equal( 'foo', self._test_shorten_bytes('foo', 3, False, None) )
    self.assert_filename_equal( 'fo', self._test_shorten_bytes('foo', 2, False, None) )
    self.assert_filename_equal( 'f', self._test_shorten_bytes('foo', 1, False, None) )

  def test_shorten_bytes_not_enough_space(self):
    with self.assertRaises(ValueError) as _:
      self._test_shorten_bytes('foo.jpg', 4, False, None)
    with self.assertRaises(ValueError) as _:
      self._test_shorten_bytes('foo.jpg', 3, False, None)

  def test_shorten_bytes_with_hash(self):
    self.assert_filename_equal( 'foo-e70422ca.jpg', self._test_shorten_bytes('foo12345678901234567890.jpg', 16, True, 8) )
    self.assert_filename_equal( 'fo-e70422ca.jpg', self._test_shorten_bytes('foo12345678901234567890.jpg', 15, True, 8) )
    self.assert_filename_equal( 'f-e70422ca.jpg', self._test_shorten_bytes('foo12345678901234567890.jpg', 14, True, 8) )
    self.assert_filename_equal( '-e70422ca.jpg', self._test_shorten_bytes('foo12345678901234567890.jpg', 13, True, 8) )

  def test_shorten_bytes_with_hash_not_enough_space(self):
    with self.assertRaises(ValueError) as _:
      self._test_shorten_bytes('foo12345678901234567890.jpg', 12, True, 8)

  def test_shorten_bytes_multibyte(self):
    # '日本語テスト.txt' = 15 chars (6 kanji/kana + . + txt), 22 bytes (6*3 + 4)
    # Each Japanese char is 3 bytes, .txt is 4 bytes
    self.assert_filename_equal( '日本語テスト.txt', self._test_shorten_bytes('日本語テスト.txt', 22, False, None) )
    # 19 bytes available: 19 - 4(.txt) = 15 stem bytes = 5 chars * 3 bytes
    self.assert_filename_equal( '日本語テス.txt', self._test_shorten_bytes('日本語テスト.txt', 19, False, None) )
    # 10 bytes available: 10 - 4(.txt) = 6 stem bytes = 2 chars * 3 bytes
    self.assert_filename_equal( '日本.txt', self._test_shorten_bytes('日本語テスト.txt', 10, False, None) )
    # 7 bytes available: 7 - 4(.txt) = 3 stem bytes = 1 char * 3 bytes
    self.assert_filename_equal( '日.txt', self._test_shorten_bytes('日本語テスト.txt', 7, False, None) )

  def test_shorten_bytes_multibyte_no_extension(self):
    # '日本語' = 9 bytes
    self.assert_filename_equal( '日本語', self._test_shorten_bytes('日本語', 9, False, None) )
    self.assert_filename_equal( '日本', self._test_shorten_bytes('日本語', 6, False, None) )
    self.assert_filename_equal( '日', self._test_shorten_bytes('日本語', 3, False, None) )

  def test_shorten_bytes_multibyte_with_hash(self):
    # '日本語テスト.txt' hash[:8] = 'cad66b86', hash_part = '-cad66b86' (9 bytes)
    # max=17: 17 - 4(.txt) = 13 available, 13 - 9(hash) = 4 stem bytes => 1 char (3 bytes) + pad? No, 1 char = 3 bytes fits
    self.assert_filename_equal( '日-cad66b86.txt', self._test_shorten_bytes('日本語テスト.txt', 17, True, 8) )
    # max=20: 20 - 4(.txt) = 16 available, 16 - 9(hash) = 7 stem bytes => 2 chars (6 bytes)
    self.assert_filename_equal( '日本-cad66b86.txt', self._test_shorten_bytes('日本語テスト.txt', 20, True, 8) )

  def test_lstrip_sep(self):
    self.assertEqual( self.native_filename('foo'), bf_filename.lstrip_sep('foo') )
    self.assertEqual( self.native_filename('foo'), bf_filename.lstrip_sep(self.native_filename('/foo')) )
    self.assertEqual( self.native_filename('foo/'), bf_filename.lstrip_sep(self.native_filename('/foo/')) )
    self.assertEqual( self.native_filename(''), bf_filename.lstrip_sep(self.native_filename('/')) )
    self.assertEqual( self.native_filename('foo.txt'), bf_filename.lstrip_sep(self.native_filename('/foo.txt')) )

  def test_rstrip_sep(self):
    self.assertEqual( self.native_filename('foo'), bf_filename.rstrip_sep(self.native_filename('foo')) )
    self.assertEqual( self.native_filename('/foo'), bf_filename.rstrip_sep(self.native_filename('/foo')) )
    self.assertEqual( self.native_filename('/foo'), bf_filename.rstrip_sep(self.native_filename('/foo/')) )
    self.assertEqual( self.native_filename(''), bf_filename.rstrip_sep(self.native_filename('/')) )

  def test_strip_sep(self):
    self.assertEqual( self.native_filename('foo'), bf_filename.strip_sep(self.native_filename('foo')) )
    self.assertEqual( self.native_filename('foo'), bf_filename.strip_sep(self.native_filename('/foo')) )
    self.assertEqual( self.native_filename('foo'), bf_filename.strip_sep(self.native_filename('/foo/')) )
    self.assertEqual( self.native_filename(''), bf_filename.strip_sep(self.native_filename('/')) )

  def test_ensure_rsep(self):
    self.assertEqual( self.native_filename('bar/'), bf_filename.ensure_rsep(self.native_filename('bar')) )
    self.assertEqual( self.native_filename('bar/'), bf_filename.ensure_rsep(self.native_filename('bar/')) )
    self.assertEqual( self.native_filename('/bar/'), bf_filename.ensure_rsep(self.native_filename('/bar/')) )
    self.assertEqual( self.native_filename('/'), bf_filename.ensure_rsep(self.native_filename('')) )
    self.assertEqual( self.native_filename('/'), bf_filename.ensure_rsep(self.native_filename('/')) )
    self.assertEqual( self.native_filename('foo/bar/'), bf_filename.ensure_rsep(self.native_filename('foo/bar')) )
    self.assertEqual( self.native_filename('/foo/bar/'), bf_filename.ensure_rsep(self.native_filename('/foo/bar')) )
    self.assertEqual( self.native_filename('foo/bar/'), bf_filename.ensure_rsep(self.native_filename('foo/bar/')) )
    self.assertEqual( self.native_filename('/foo/bar/'), bf_filename.ensure_rsep(self.native_filename('/foo/bar/')) )

  def test_ensure_lsep(self):
    self.assertEqual( self.native_filename('/bar'), bf_filename.ensure_lsep(self.native_filename('bar')) )
    self.assertEqual( self.native_filename('/bar/'), bf_filename.ensure_lsep(self.native_filename('bar/')) )
    self.assertEqual( self.native_filename('/bar'), bf_filename.ensure_lsep(self.native_filename('/bar')) )
    self.assertEqual( self.native_filename('/bar/'), bf_filename.ensure_lsep(self.native_filename('/bar/')) )
    self.assertEqual( self.native_filename('/'), bf_filename.ensure_lsep(self.native_filename('')) )
    self.assertEqual( self.native_filename('/'), bf_filename.ensure_lsep(self.native_filename('/')) )
    self.assertEqual( self.native_filename('/foo/bar'), bf_filename.ensure_lsep(self.native_filename('foo/bar')) )
    self.assertEqual( self.native_filename('/foo/bar/'), bf_filename.ensure_lsep(self.native_filename('foo/bar/')) )

  def test_remove_head(self):
    self.assertEqual( self.native_filename('bar'), bf_filename.remove_head(self.native_filename('foo/bar'), self.native_filename('foo')) )
    self.assertEqual( self.native_filename('bar/baz'), bf_filename.remove_head(self.native_filename('foo/bar/baz'), self.native_filename('foo')) )
    self.assertEqual( self.native_filename('foo'), bf_filename.remove_head(self.native_filename('foo'), self.native_filename('foo/')) )
    self.assertEqual( self.native_filename('foo'), bf_filename.remove_head(self.native_filename('foo'), self.native_filename('foo')) )
    self.assertEqual( self.native_filename(''), bf_filename.remove_head(self.native_filename('foo/'), self.native_filename('foo/')) )

  def test_remove_tail(self):
    self.assertEqual( self.native_filename('/foo'), bf_filename.remove_tail(self.native_filename('/foo/bar'), self.native_filename('bar')) )
    self.assertEqual( self.native_filename('foo'), bf_filename.remove_tail(self.native_filename('foo/bar'), self.native_filename('bar')) )
    self.assertEqual( self.native_filename('foo'), bf_filename.remove_tail(self.native_filename('foo/bar'), self.native_filename('/bar')) )
    
if __name__ == '__main__':
  unit_test.main()

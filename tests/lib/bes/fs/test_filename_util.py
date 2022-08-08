#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from bes.fs.filename_util import filename_util

class test_filename_util(unit_test):

  def test_extension(self):
    self.assertEqual( None, filename_util.extension('a') )
    self.assertEqual( 'foo', filename_util.extension('a.foo') )
    self.assertEqual( 'gz', filename_util.extension('a.tar.gz') )
    self.assertEqual( 'png', filename_util.extension('.kiwi.png') )
    self.assertEqual( '', filename_util.extension('a.') )

  def test_has_extension(self):
    self.assertTrue( filename_util.has_extension('a.foo', 'foo') )
    self.assertFalse( filename_util.has_extension('a.foo', 'png') )

  def test_has_extension_with_ignore_case(self):
    self.assertTrue( filename_util.has_extension('a.foo', 'Foo', ignore_case = True) )
    self.assertFalse( filename_util.has_extension('a.foo', 'PNG', ignore_case = True) )
    self.assertFalse( filename_util.has_extension('a.foo', 'Foo', ignore_case = False) )
    
  def test_has_any_extension(self):
    self.assertTrue( filename_util.has_any_extension('a.foo', ( 'foo', 'png' )) )
    self.assertFalse( filename_util.has_any_extension('a.foo', ( 'png', 'jpg' )) )
    self.assertFalse( filename_util.has_any_extension('python3.7', ( 'exe', 'bat', 'cmd', 'ps1' )) )
    
  def test_has_any_extension_ignore_case(self):
    self.assertFalse( filename_util.has_any_extension('FOO.EXE', ( 'exe', 'bat' )) )
    self.assertTrue( filename_util.has_any_extension('FOO.EXE', ( 'exe', 'bat' ), ignore_case = True ) )
    self.assertFalse( filename_util.has_any_extension('python3.7', ( 'exe', 'bat', 'cmd', 'ps1' ), ignore_case = True) )
    
  def test_without_extension(self):
    self.assertEqual( 'a', filename_util.without_extension('a.foo') )
    self.assertEqual( 'a', filename_util.without_extension('a') )
    self.assertEqual( '.kiwi', filename_util.without_extension('.kiwi.png') )

  def test_split_extension(self):
    self.assertEqual( ( 'a', 'foo' ), filename_util.split_extension('a.foo') )
    self.assertEqual( ( 'a', None ), filename_util.split_extension('a') )
    self.assertEqual( ( '.kiwi', 'png' ), filename_util.split_extension('.kiwi.png') )
    self.assertEqual( ( 'a' , None ), filename_util.split_extension('a') )
    self.assertEqual( ( 'a', 'foo' ), filename_util.split_extension('a.foo') )
    self.assertEqual( ( 'a.tar', 'gz' ), filename_util.split_extension('a.tar.gz') )
    self.assertEqual( ( '.kiwi', 'png' ), filename_util.split_extension('.kiwi.png') )
    self.assertEqual( ( 'a', '' ), filename_util.split_extension('a.') )

  def test_prefix(self):
    self.assertEqual( None, filename_util.prefix('foo.txt') )
    self.assertEqual( None, filename_util.prefix('foo-.txt') )
    self.assertEqual( 'foo', filename_util.prefix('foo-42.txt') )
    self.assertEqual( None, filename_util.prefix('') )

  def test_add_extension(self):
    self.assertEqual( 'foo.txt', filename_util.add_extension('foo', 'txt') )
    self.assertEqual( 'foo', filename_util.add_extension('foo', '') )
    self.assertEqual( 'foo', filename_util.add_extension('foo', None) )
    self.assertEqual( '.txt', filename_util.add_extension('', 'txt') )

  def test_replace_extension(self):
    self.assertEqual( 'foo.txt', filename_util.replace_extension('foo.jpg', 'txt') )
    self.assertEqual( 'something.jpg.foo.txt', filename_util.replace_extension('something.jpg.foo.jpg', 'txt') )
    self.assertEqual( 'something', filename_util.replace_extension('something', 'txt') )
    self.assertEqual( '', filename_util.replace_extension('', 'txt') )
    self.assertEqual( 'foo.txt', filename_util.replace_extension('foo.txt', 'txt') )

  @classmethod
  def _test_shorten(clazz, filename, max_length, include_hash, hash_length):
    return filename_util.shorten(filename,
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
    
if __name__ == '__main__':
  unit_test.main()

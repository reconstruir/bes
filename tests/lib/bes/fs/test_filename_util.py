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
    
if __name__ == '__main__':
  unit_test.main()

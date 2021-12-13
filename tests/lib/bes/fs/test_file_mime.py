#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
import sys
from os import path

from bes.testing.unit_test import unit_test
from bes.fs.file_mime import file_mime
from bes.fs.file_symlink import file_symlink
from bes.testing.unit_test_function_skip import unit_test_function_skip

from _bes_unit_test_common.unit_test_media import unit_test_media

class test_file_mime(unit_test):

  def test_mime_type(self):
    tmp = self.make_temp_file(content = 'this is text\n', suffix = '.txt')
    mt = file_mime.mime_type(tmp)
    self.assertEqual( 'text/plain', mt.mime_type )
    if mt.charset:
      self.assertEqual( 'us-ascii', mt.charset )

  def test_is_false(self):
    self.assertFalse( file_mime.is_binary(self.make_temp_file(content = 'this is text\n', suffix = '.txt')) )
    
  @unit_test_function_skip.skip_if_not_unix()
  def test_is_binary_unix(self):
    self.assertTrue( file_mime.is_binary(file_symlink.resolve('/bin/sh')) )
    
  @unit_test_function_skip.skip_if_not_windows()
  def test_is_binary_windows(self):
    self.assertTrue( file_mime.is_binary(sys.executable) )
    
  def test_is_text(self):
    self.assertTrue( file_mime.is_text(self.make_temp_file(content = 'this is text\n', suffix = '.txt')) )

  def test_content_is_text_true(self):
    self.assertTrue( file_mime.content_is_text(self.make_temp_file(content = 'this is text\n', suffix = '.txt')) )
    
  def test_content_is_text_false(self):
    self.assertFalse( file_mime.content_is_text(self.make_temp_file(content = unit_test_media.PNG_SMALLEST_POSSIBLE, suffix = '.png')) )

  def test_png(self):
    png = self.make_temp_file(content = unit_test_media.PNG_SMALLEST_POSSIBLE, suffix = '.png')
    self.assertEqual( ( 'image/png', 'binary' ), file_mime.mime_type(png) )

  def test_jpg(self):
    jpg = self.make_temp_file(content = unit_test_media.JPG_SMALLEST_POSSIBLE, suffix = '.jpg')
    self.assertEqual( ( 'image/jpeg', 'binary' ), file_mime.mime_type(jpg) )

  def test_mp4(self):
    mp4 = self.make_temp_file(content = unit_test_media.MP4_SMALLEST_POSSIBLE, suffix = '.mp4')
    self.assertEqual( ( 'video/mp4', 'binary' ), file_mime.mime_type(mp4) )
    
  @unit_test_function_skip.skip_if_not_unix()
  def test_is_text_false_unix(self):
    self.assertFalse( file_mime.is_text(file_symlink.resolve('/bin/sh')) )

if __name__ == '__main__':
  unit_test.main()

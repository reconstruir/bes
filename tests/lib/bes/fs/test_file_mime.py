#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
import sys
from os import path

from bes.testing.unit_test import unit_test
from bes.fs.file_mime import file_mime
from bes.fs.file_symlink import file_symlink
from bes.testing.unit_test_function_skip import unit_test_function_skip
from bes.property.cached_property import cached_property

from _bes_unit_test_common.unit_test_media import unit_test_media

class test_file_mime(unit_test):

  @cached_property
  def _png_file(self):
    return self.make_temp_file(content = unit_test_media.PNG_SMALLEST_POSSIBLE, suffix = '.png')
  
  @cached_property
  def _png_file_wrong_extension(self):
    return self.make_temp_file(content = unit_test_media.PNG_SMALLEST_POSSIBLE, suffix = '.txt')

  @cached_property
  def _jpg_file(self):
    return self.make_temp_file(content = unit_test_media.JPG_SMALLEST_POSSIBLE, suffix = '.jpg')
  
  @cached_property
  def _jpg_file_wrong_extension(self):
    return self.make_temp_file(content = unit_test_media.JPG_SMALLEST_POSSIBLE, suffix = '.txt')

  @cached_property
  def _mp4_file(self):
    return self.make_temp_file(content = unit_test_media.MP4_SMALLEST_POSSIBLE, suffix = '.mp4')
  
  @cached_property
  def _mp4_file_wrong_extension(self):
    return self.make_temp_file(content = unit_test_media.MP4_SMALLEST_POSSIBLE, suffix = '.txt')
  
  def test_mime_type(self):
    tmp = self.make_temp_file(content = 'this is text\n', suffix = '.txt')
    mt = file_mime.mime_type(tmp)
    self.assertEqual( 'text/plain', mt.mime_type )
    if mt.charset:
      self.assertEqual( 'us-ascii', mt.charset )

  def test_is_binary_false(self):
    self.assertFalse( file_mime.is_binary(self.make_temp_file(content = 'this is text\n', suffix = '.txt')) )
    
  @unit_test_function_skip.skip_if_not_unix()
  def test_is_binary_unix(self):
    self.assertTrue( file_mime.is_binary(file_symlink.resolve('/bin/sh')) )
    
  @unit_test_function_skip.skip_if_not_windows()
  def test_is_binary_windows(self):
    self.assertTrue( file_mime.is_binary(sys.executable) )
    
  def test_is_text_true(self):
    self.assertTrue( file_mime.is_text(self.make_temp_file(content = 'this is text\n', suffix = '.txt')) )

  def test_is_text_false(self):
    self.assertFalse( file_mime.is_text(self._png_file) )
    
  def test_content_is_text_true(self):
    self.assertTrue( file_mime.content_is_text(self.make_temp_file(content = 'this is text\n', suffix = '.txt')) )
    
  def test_content_is_text_false(self):
    self.assertFalse( file_mime.content_is_text(self.make_temp_file(content = unit_test_media.PNG_SMALLEST_POSSIBLE, suffix = '.png')) )

  def test_png(self):
    self.assertEqual( 'image/png', file_mime.mime_type(self._png_file).mime_type )

  @unit_test_function_skip.skip_if_not_unix(warning = True)
  def test_png_wrong_extension(self):
    self.assertEqual( 'image/png', file_mime.mime_type(self._png_file_wrong_extension).mime_type )
    
  def test_jpg(self):
    self.assertEqual( 'image/jpeg', file_mime.mime_type(self._jpg_file).mime_type )

  @unit_test_function_skip.skip_if_not_unix(warning = True)
  def test_jpg_wrong_extension(self):
    self.assertEqual( 'image/jpeg', file_mime.mime_type(self._jpg_file_wrong_extension).mime_type )

  def test_mp4(self):
    self.assertEqual( 'video/mp4', file_mime.mime_type(self._mp4_file).mime_type )

  @unit_test_function_skip.skip_if_not_unix(warning = True)
  def test_mp4_wrong_extension(self):
    self.assertEqual( 'video/mp4', file_mime.mime_type(self._mp4_file_wrong_extension).mime_type )

  def test_media_type(self):
    self.assertEqual( 'video', file_mime.media_type(self._mp4_file) )
    self.assertEqual( 'image', file_mime.media_type(self._png_file) )
    self.assertEqual( 'image', file_mime.media_type(self._jpg_file) )
    self.assertEqual( 'unknown', file_mime.media_type(self.make_temp_file(content = 'this is foo.\n')) )
    
if __name__ == '__main__':
  unit_test.main()

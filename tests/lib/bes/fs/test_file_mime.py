#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import sys
from os import path

from bes.testing.unit_test import unit_test
from bes.fs.file_mime import file_mime
from bes.fs.file_symlink import file_symlink
from bes.testing.unit_test_function_skip import unit_test_function_skip
from bes.property.cached_property import cached_property

from _bes_unit_test_common.unit_test_media_files import unit_test_media_files

class test_file_mime(unit_test, unit_test_media_files):

  def test_mime_type(self):
    tmp = self.make_temp_file(content = 'this is text\n', suffix = '.txt')
    self.assertEqual( 'text/plain', file_mime.mime_type(tmp) )

  def test_is_binary_false(self):
    self.assertFalse( file_mime.is_binary(self.make_temp_file(content = 'this is text\n', suffix = '.txt')) )
    
  @unit_test_function_skip.skip_if_not_windows()
  def test_is_binary_windows(self):
    self.assertTrue( file_mime.is_binary(sys.executable) )
    
  def test_is_text_true(self):
    self.assertTrue( file_mime.is_text(self.make_temp_file(content = 'this is text\n', suffix = '.txt')) )

  def test_is_text_false(self):
    self.assertFalse( file_mime.is_text(self.png_file) )
    
  def test_png(self):
    self.assertEqual( 'image/png', file_mime.mime_type(self.png_file) )

  @unit_test_function_skip.skip_if_not_unix(warning = True)
  def test_png_wrong_extension(self):
    self.assertEqual( 'image/png', file_mime.mime_type(self.png_file_wrong_extension) )
    
  def test_jpg(self):
    self.assertEqual( 'image/jpeg', file_mime.mime_type(self.jpg_file) )

  @unit_test_function_skip.skip_if_not_unix(warning = True)
  def test_jpg_wrong_extension(self):
    self.assertEqual( 'image/jpeg', file_mime.mime_type(self.jpg_file_wrong_extension) )

  def test_mp4(self):
    self.assertEqual( 'video/mp4', file_mime.mime_type(self.mp4_file) )

  @unit_test_function_skip.skip_if_not_unix(warning = True)
  def test_mp4_wrong_extension(self):
    self.assertEqual( 'video/mp4', file_mime.mime_type(self.mp4_file_wrong_extension) )

  def test_media_type(self):
    self.assertEqual( 'video', file_mime.media_type_for_file(self.mp4_file) )
    self.assertEqual( 'image', file_mime.media_type_for_file(self.png_file) )
    self.assertEqual( 'image', file_mime.media_type_for_file(self.jpg_file) )
    self.assertEqual( 'audio', file_mime.media_type_for_file(self.wav_file) )
    self.assertEqual( 'audio', file_mime.media_type_for_file(self.mp3_file) )
    self.assertEqual( 'audio', file_mime.media_type_for_file(self.flac_file) )
    self.assertEqual( None, file_mime.media_type_for_file(self.unknown_file) )

  @unit_test_function_skip.skip_if_not_unix(warning = True)
  def test_media_type_wrong_extension(self):
    self.assertEqual( 'video', file_mime.media_type_for_file(self.mp4_file_wrong_extension) )
    self.assertEqual( 'image', file_mime.media_type_for_file(self.png_file_wrong_extension) )
    self.assertEqual( 'image', file_mime.media_type_for_file(self.jpg_file_wrong_extension) )
    
    self.assertEqual( None, file_mime.media_type_for_file(self.unknown_file_png_extension) )
    self.assertEqual( None, file_mime.media_type_for_file(self.unknown_file_jpg_extension) )
    self.assertEqual( None, file_mime.media_type_for_file(self.unknown_file_mp4_extension) )
    self.assertEqual( None, file_mime.media_type_for_file(self.unknown_file_txt_extension) )

  def test_wav(self):
    self.assertEqual( True, file_mime.mime_type(self.wav_file) in ( 'audio/wav', 'audio/x-wav', 'audio/wave' ) )

  def test_mp3(self):
    self.assertEqual( True, file_mime.mime_type(self.mp3_file) in ( 'audio/mpeg', 'audio/mpegaudio/mpeg' ) )

  def test_flac(self):
    self.assertTrue( True, file_mime.mime_type(self.flac_file) in ( 'audio/flac', 'audio/x-flac' ) )
    
if __name__ == '__main__':
  unit_test.main()

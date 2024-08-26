#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import sys
from os import path

from bes.testing.unit_test import unit_test
from bes.files.mime.bf_mime import bf_mime
from bes.files.bf_symlink import bf_symlink
from bes.testing.unit_test_function_skip import unit_test_function_skip
from bes.property.cached_property import cached_property

from _bes_unit_test_common.unit_test_media_files import unit_test_media_files

class test_bf_mime(unit_test, unit_test_media_files):

  def test_mime_type(self):
    tmp = self.make_temp_file(content = 'this is text\n', suffix = '.txt')
    self.assertEqual( 'text/plain', bf_mime.mime_type(tmp) )

  def test_is_binary_false(self):
    self.assertFalse( bf_mime.is_binary(self.make_temp_file(content = 'this is text\n', suffix = '.txt')) )
    
  @unit_test_function_skip.skip_if_not_unix()
  def test_is_binary_unix(self):
    self.assertTrue( bf_mime.is_binary(bf_symlink.resolve('/bin/sh')) )
    
  @unit_test_function_skip.skip_if_not_windows()
  def test_is_binary_windows(self):
    self.assertTrue( bf_mime.is_binary(sys.executable) )
    
  def test_is_text_true(self):
    self.assertTrue( bf_mime.is_text(self.make_temp_file(content = 'this is text\n', suffix = '.txt')) )

  def test_is_text_false(self):
    self.assertFalse( bf_mime.is_text(self.png_file) )
    
  def test_png(self):
    self.assertEqual( 'image/png', bf_mime.mime_type(self.png_file) )

  @unit_test_function_skip.skip_if_not_unix(warning = True)
  def test_png_wrong_extension(self):
    self.assertEqual( 'image/png', bf_mime.mime_type(self.png_file_wrong_extension) )
    
  def test_jpg(self):
    self.assertEqual( 'image/jpeg', bf_mime.mime_type(self.jpg_file) )

  @unit_test_function_skip.skip_if_not_unix(warning = True)
  def test_jpg_wrong_extension(self):
    self.assertEqual( 'image/jpeg', bf_mime.mime_type(self.jpg_file_wrong_extension) )

  def test_mp4(self):
    self.assertEqual( 'video/mp4', bf_mime.mime_type(self.mp4_file) )

  @unit_test_function_skip.skip_if_not_unix(warning = True)
  def test_mp4_wrong_extension(self):
    self.assertEqual( 'video/mp4', bf_mime.mime_type(self.mp4_file_wrong_extension) )

  def test_media_type(self):
    self.assertEqual( 'video', bf_mime.media_type_for_file(self.mp4_file) )
    self.assertEqual( 'image', bf_mime.media_type_for_file(self.png_file) )
    self.assertEqual( 'image', bf_mime.media_type_for_file(self.jpg_file) )
    self.assertEqual( 'audio', bf_mime.media_type_for_file(self.wav_file) )
    self.assertEqual( 'audio', bf_mime.media_type_for_file(self.mp3_file) )
    self.assertEqual( 'audio', bf_mime.media_type_for_file(self.flac_file) )
    self.assertEqual( None, bf_mime.media_type_for_file(self.unknown_file) )

  @unit_test_function_skip.skip_if_not_unix(warning = True)
  def test_media_type_wrong_extension(self):
    self.assertEqual( 'video', bf_mime.media_type_for_file(self.mp4_file_wrong_extension) )
    self.assertEqual( 'image', bf_mime.media_type_for_file(self.png_file_wrong_extension) )
    self.assertEqual( 'image', bf_mime.media_type_for_file(self.jpg_file_wrong_extension) )
    
    self.assertEqual( None, bf_mime.media_type_for_file(self.unknown_file_png_extension) )
    self.assertEqual( None, bf_mime.media_type_for_file(self.unknown_file_jpg_extension) )
    self.assertEqual( None, bf_mime.media_type_for_file(self.unknown_file_mp4_extension) )
    self.assertEqual( None, bf_mime.media_type_for_file(self.unknown_file_txt_extension) )

  def test_wav(self):
    self.assertEqual( True, bf_mime.mime_type(self.wav_file) in ( 'audio/wav', 'audio/x-wav')  )

  def test_mp3(self):
    self.assertEqual( True, bf_mime.mime_type(self.mp3_file) in ( 'audio/mpeg', 'audio/mpegaudio/mpeg')  )

  def test_flac(self):
    self.assertEqual( 'audio/flac', bf_mime.mime_type(self.flac_file) )
    
if __name__ == '__main__':
  unit_test.main()

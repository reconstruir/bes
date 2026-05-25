#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test

from _bes_unit_test_common.unit_test_media import unit_test_media
from _bes_unit_test_common.unit_test_media_files import unit_test_media_files

def make_test_case(impl):

  class _file_mime_type_detector_tester(unit_test, unit_test_media_files):

    # --- text / structured text ---

    def test_text_plain(self):
      tmp = self.make_temp_file(content = 'this is text\n', suffix = '.txt')
      self.assertEqual( 'text/plain', impl.detect_mime_type(tmp) )

    def test_xml(self):
      tmp = self.make_temp_file(content = '<?xml version="1.0"?>\n<root/>\n', suffix = '.xml')
      self.assertIn( impl.detect_mime_type(tmp), ('application/xml', 'text/xml') )

    def test_html(self):
      tmp = self.make_temp_file(content = '<!DOCTYPE html>\n<html><body></body></html>\n', suffix = '.html')
      self.assertEqual( 'text/html', impl.detect_mime_type(tmp) )

    def test_json(self):
      tmp = self.make_temp_file(content = '{"key": "value"}\n', suffix = '.json')
      self.assertEqual( 'application/json', impl.detect_mime_type(tmp) )

    # --- images ---

    def test_png(self):
      self.assertEqual( 'image/png', impl.detect_mime_type(self.png_file) )

    def test_jpg(self):
      self.assertEqual( 'image/jpeg', impl.detect_mime_type(self.jpg_file) )

    # --- video ---

    def test_mp4(self):
      self.assertEqual( 'video/mp4', impl.detect_mime_type(self.mp4_file) )

    # --- audio ---

    def test_mp3(self):
      self.assertEqual( 'audio/mpeg', impl.detect_mime_type(self.mp3_file) )

    def test_wav(self):
      self.assertIn( impl.detect_mime_type(self.wav_file), ('audio/wave', 'audio/x-wav', 'audio/wav') )

    def test_flac(self):
      self.assertIn( impl.detect_mime_type(self.flac_file), ('audio/flac', 'audio/x-flac') )

    # --- archives ---

    def test_zip(self):
      self.assertEqual( 'application/zip', impl.detect_mime_type(self.zip_file) )

    def test_xz(self):
      self.assertEqual( 'application/x-xz', impl.detect_mime_type(self.xz_file) )

    # --- executables ---

    def test_windows_exe(self):
      self.assertIn( impl.detect_mime_type(self.windows_exe_file),
        ('application/x-dosexec',
         'application/x-msdownload',
         'application/vnd.microsoft.portable-executable') )

    # --- wrong-extension (magic beats extension) ---

    def test_wrong_png_extension(self):
      self.assertEqual( 'image/png', impl.detect_mime_type(self.png_file_wrong_extension) )

    def test_wrong_jpg_extension(self):
      self.assertEqual( 'image/jpeg', impl.detect_mime_type(self.jpg_file_wrong_extension) )

    def test_wrong_mp4_extension(self):
      self.assertEqual( 'video/mp4', impl.detect_mime_type(self.mp4_file_wrong_extension) )

    def test_wrong_xz_extension(self):
      self.assertEqual( 'application/x-xz', impl.detect_mime_type(self.xz_file_wrong_extension) )

    # --- unknown / unrecognised ---

    def test_unknown_returns_none(self):
      self.assertIsNone( impl.detect_mime_type(self.unknown_file) )

  return _file_mime_type_detector_tester

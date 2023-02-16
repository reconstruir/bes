#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.testing.unit_test import unit_test
from bes.testing.unit_test_function_skip import unit_test_function_skip

from _bes_unit_test_common.unit_test_media import unit_test_media
from _bes_unit_test_common.unit_test_media_files import unit_test_media_files

def make_test_case(impl):
  
  class _file_mime_type_detector_tester(unit_test, unit_test_media_files):

    def test_text_plain(self):
      tmp = self.make_temp_file(content = 'this is text\n', suffix = '.txt')
      self.assertEqual( 'text/plain', impl.detect_mime_type(tmp) )

    def test_png(self):
      self.assertEqual( 'image/png', impl.detect_mime_type(self.png_file) )
  
    @unit_test_function_skip.skip_if_not_unix(warning = True)
    def xtest_wrong_png_extension(self):
      self.assertEqual( 'image/png', impl.detect_mime_type(self.png_file_wrong_extension) )
      
    def xtest_jpg(self):
      self.assertEqual( 'image/jpeg', impl.detect_mime_type(self.jpg_file) )
  
    @unit_test_function_skip.skip_if_not_unix(warning = True)
    def xtest_wrong_jpg_extension(self):
      self.assertEqual( 'image/jpeg', impl.detect_mime_type(self.jpg_file_wrong_extension) )
  
    def xtest_mp4(self):
      self.assertEqual( 'video/mp4', impl.detect_mime_type(self.mp4_file) )
  
    @unit_test_function_skip.skip_if_not_unix(warning = True)
    def xtest_wrong_mp4_extension(self):
      self.assertEqual( 'video/mp4', impl.detect_mime_type(self.mp4_file_wrong_extension) )
  
  return _file_mime_type_detector_tester

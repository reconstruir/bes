#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.fs._detail._bfile_mime_type_detector_cheesy import _bfile_mime_type_detector_cheesy
from bes.testing.unit_test_class_skip import unit_test_class_skip

from _bes_unit_test_common.unit_test_media import unit_test_media
from _bes_unit_test_common.unit_test_media_files import unit_test_media_files

class test__bfile_mime_type_detector_magic(unit_test, unit_test_media_files):

  @classmethod
  def setUpClass(clazz):
    unit_test_class_skip.raise_skip_if(_bfile_mime_type_detector_cheesy.is_supported(), 'not supported')

  def test_png(self):
    self.assertEqual( 'image/png', _bfile_mime_type_detector_cheesy.detect_mime_type(self.png_file) )

  def test_jpg(self):
    self.assertEqual( 'image/jpeg', _bfile_mime_type_detector_cheesy.detect_mime_type(self.jpg_file) )

  def test_mp4(self):
    self.assertEqual( 'video/mp4', _bfile_mime_type_detector_cheesy.detect_mime_type(self.mp4_file) )
    
if __name__ == '__main__':
  unit_test.main()
    

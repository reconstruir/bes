#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import sys

from bes.testing.unit_test import unit_test
from bes.files.mime._detail._bf_mime_type_detector_cheesy import _bf_mime_type_detector_cheesy
from bes.testing.unit_test_class_skip import unit_test_class_skip
from bes.testing.unit_test_function_skip import unit_test_function_skip
from bes.system.which import which

from _bes_unit_test_common.unit_test_media import unit_test_media
from _bes_unit_test_common.unit_test_media_files import unit_test_media_files

class test__bf_mime_type_detector_magic(unit_test, unit_test_media_files):

  @classmethod
  def setUpClass(clazz):
    unit_test_class_skip.raise_skip_if(_bf_mime_type_detector_cheesy.is_supported(), 'not supported')

  def test_png(self):
    self.assertEqual( 'image/png', _bf_mime_type_detector_cheesy.detect_mime_type(self.png_file) )

  def test_jpg(self):
    self.assertEqual( 'image/jpeg', _bf_mime_type_detector_cheesy.detect_mime_type(self.jpg_file) )

  def test_mp4(self):
    self.assertEqual( 'video/mp4', _bf_mime_type_detector_cheesy.detect_mime_type(self.mp4_file) )

  def test_zip(self):
    self.assertEqual( 'application/zip', _bf_mime_type_detector_cheesy.detect_mime_type(self.zip_file) )

  def test_xz(self):
    self.assertEqual( 'application/x-xz', _bf_mime_type_detector_cheesy.detect_mime_type(self.xz_file) )

  def test_unknown_returns_none(self):
    self.assertIsNone( _bf_mime_type_detector_cheesy.detect_mime_type(self.unknown_file) )

  def test_elf(self):
    tmp = self.make_temp_file(content = b'\x7fELF\x02\x01\x01\x00' + b'\x00' * 8)
    self.assertEqual( 'application/x-elf', _bf_mime_type_detector_cheesy.detect_mime_type(tmp) )

  def test_macho_64(self):
    tmp = self.make_temp_file(content = b'\xcf\xfa\xed\xfe' + b'\x00' * 12)
    self.assertEqual( 'application/x-mach-binary', _bf_mime_type_detector_cheesy.detect_mime_type(tmp) )

  def test_macho_fat(self):
    tmp = self.make_temp_file(content = b'\xca\xfe\xba\xbe' + b'\x00' * 12)
    self.assertEqual( 'application/x-mach-binary', _bf_mime_type_detector_cheesy.detect_mime_type(tmp) )

  def test_dosexec(self):
    tmp = self.make_temp_file(content = b'\x4d\x5a' + b'\x00' * 14)
    self.assertEqual( 'application/x-dosexec', _bf_mime_type_detector_cheesy.detect_mime_type(tmp) )

  @unit_test_function_skip.skip_if_not_unix()
  def test_real_binary(self):
    shell = which.which('bash') or which.which('zsh') or which.which('dash')
    if not shell:
      return
    result = _bf_mime_type_detector_cheesy.detect_mime_type(shell)
    self.assertIn(result, ('application/x-mach-binary', 'application/x-elf'))

if __name__ == '__main__':
  unit_test.main()
    

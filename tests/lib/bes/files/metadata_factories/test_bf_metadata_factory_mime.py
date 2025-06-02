#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
import os.path as path
import time

from bes.testing.unit_test import unit_test
from bes.files.metadata.bf_metadata_factory_registry import bf_metadata_factory_registry
from bes.files.metadata.bf_metadata import bf_metadata
from bes.files.metadata_factories.bf_metadata_factory_mime import bf_metadata_factory_mime
from bes.files.mime.bf_mime import bf_mime
from bes.files.bf_date import bf_date

from _bes_unit_test_common.unit_test_media import unit_test_media
from _bes_unit_test_common.unit_test_media_files import unit_test_media_files

class test_bf_metadata_factory_mime(unit_test, unit_test_media_files):

  @classmethod
  def setUpClass(clazz):
    bf_metadata_factory_registry.register_factory(bf_metadata_factory_mime)

  def test_get_mime_type_jpeg(self):
    tmp = self.make_temp_file(dir = __file__, content = self.jpg_file, suffix = '.jpg')
    self.assertEqual( 'image/jpeg',
                      bf_metadata.get_metadata(tmp, 'bes__mime__mime_type__1.0') )

  def test_get_mime_type_png(self):
    tmp = self.make_temp_file(dir = __file__, content = self.png_file, suffix = '.png')
    self.assertEqual( 'image/png',
                      bf_metadata.get_metadata(tmp, 'bes__mime__mime_type__1.0') )

  def test_get_media_type_image_jpg(self):
    tmp = self.make_temp_file(dir = __file__, content = self.jpg_file, suffix = '.jpg')
    self.assertEqual( 'image',
                      bf_metadata.get_metadata(tmp, 'bes__mime__media_type__1.0') )

  def test_get_media_type_image_png(self):
    tmp = self.make_temp_file(dir = __file__, content = self.png_file, suffix = '.png')
    self.assertEqual( 'image',
                      bf_metadata.get_metadata(tmp, 'bes__mime__media_type__1.0') )

  def test_get_media_type_video_mp4(self):
    tmp = self.make_temp_file(dir = __file__, content = self.mp4_file, suffix = '.mp4')
    self.assertEqual( 'video',
                      bf_metadata.get_metadata(tmp, 'bes__mime__media_type__1.0') )

  def test_get_media_type_unknown(self):
    tmp = self.make_temp_file(dir = __file__, content = self.unknown_file, suffix = '.unknown')
    self.assertEqual( 'unknown',
                      bf_metadata.get_metadata(tmp, 'bes__mime__media_type__1.0') )
    
  def test_get_mime_type_change(self):
    tmp = self.make_temp_file(dir = __file__, non_existent = True, suffix = '.png')
    with open(tmp, 'wb') as fout:
      with open(self.png_file, 'rb') as png_file:
        fout.write(png_file.read())
      fout.flush()
      os.fsync(fout.fileno())
      self.assertEqual( 'image/png', bf_metadata.get_metadata(tmp, 'bes__mime__mime_type__1.0') )

      time.sleep(0.01)
      with open(self.jpg_file, 'rb') as jpg_file:
        fout.seek(0)
        fout.truncate(0)
        fout.write(jpg_file.read())
        fout.flush()
        os.fsync(fout.fileno())
      
      self.assertEqual( 'image/jpeg', bf_metadata.get_metadata(tmp, 'bes__mime__mime_type__1.0') )

if __name__ == '__main__':
  unit_test.main()

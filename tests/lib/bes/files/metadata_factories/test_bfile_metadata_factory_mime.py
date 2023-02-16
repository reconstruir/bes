#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.testing.unit_test import unit_test
from bes.files.metadata.bfile_metadata_factory_registry import bfile_metadata_factory_registry
from bes.files.metadata.bfile_metadata import bfile_metadata
from bes.files.metadata_factories.bfile_metadata_factory_mime import bfile_metadata_factory_mime
from bes.files.mime.bfile_mime import bfile_mime
from bes.files.bfile_date import bfile_date

from _bes_unit_test_common.unit_test_media import unit_test_media
from _bes_unit_test_common.unit_test_media_files import unit_test_media_files

class test_bfile_metadata_factory_mime(unit_test, unit_test_media_files):

  @classmethod
  def setUpClass(clazz):
    bfile_metadata_factory_registry.register_factory(bfile_metadata_factory_mime)

  @classmethod
  def tearDownClass(clazz):
    bfile_metadata_factory_registry.unregister_factory(bfile_metadata_factory_mime)
  
  def test_get_mime_type_jpeg(self):
    tmp = self.make_temp_file(dir = __file__, content = self.jpg_file, suffix = '.jpg')
    self.assertEqual( 'image/jpeg',
                      bfile_metadata.get_metadata(tmp, 'bes', 'mime', 'mime_type', '1.0') )

  def test_get_mime_type_png(self):
    tmp = self.make_temp_file(dir = __file__, content = self.png_file, suffix = '.png')
    self.assertEqual( 'image/png', bfile_metadata.get_metadata(tmp, 'bes', 'mime', 'mime_type', '1.0') )

  def test_get_media_type_image_jpg(self):
    tmp = self.make_temp_file(dir = __file__, content = self.jpg_file, suffix = '.jpg')
    self.assertEqual( 'image', bfile_metadata.get_metadata(tmp, 'bes', 'mime', 'media_type', '1.0') )

  def test_get_media_type_image_png(self):
    tmp = self.make_temp_file(dir = __file__, content = self.png_file, suffix = '.png')
    self.assertEqual( 'image', bfile_metadata.get_metadata(tmp, 'bes', 'mime', 'media_type', '1.0') )

  def test_get_media_type_video_mp4(self):
    tmp = self.make_temp_file(dir = __file__, content = self.mp4_file, suffix = '.mp4')
    self.assertEqual( 'video', bfile_metadata.get_metadata(tmp, 'bes', 'mime', 'media_type', '1.0') )

  def test_get_media_type_unknown(self):
    tmp = self.make_temp_file(dir = __file__, content = self.unknown_file, suffix = '.unknown')
    self.assertEqual( 'unknown', bfile_metadata.get_metadata(tmp, 'bes', 'mime', 'media_type', '1.0') )
    
  def test_get_mime_type_change(self):
    tmp = self.make_temp_file(dir = __file__, content = self.png_file, suffix = '.png')
    self.assertEqual( 'image/png', bfile_metadata.get_metadata(tmp, 'bes', 'mime', 'mime_type', '1.0') )
    with open(tmp, 'wb') as to_file:
      with open(self.jpg_file, 'rb') as from_file:
        to_file.write(from_file.read())
      to_file.flush()
    bfile_date.touch(tmp)
    self.assertEqual( 'image/jpeg', bfile_metadata.get_metadata(tmp, 'bes', 'mime', 'mime_type', '1.0') )

if __name__ == '__main__':
  unit_test.main()

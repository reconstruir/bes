#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.testing.unit_test import unit_test
from bes.files.metadata.bfile_metadata_factory_registry import bfile_metadata_factory_registry
from bes.files.metadata.bfile_metadata import bfile_metadata
from bes.files.metadata_factories.bfile_metadata_factory_mime import bfile_metadata_factory_mime
from bes.files.mime.bfile_mime import bfile_mime

from _bes_unit_test_common.unit_test_media import unit_test_media
from _bes_unit_test_common.unit_test_media_files import unit_test_media_files

class test_bfile_metadata_factory_mime(unit_test, unit_test_media_files):

  # Use a temporary directory in the same filesystem as the code to avoid the
  # issue that on some platforms the tmp dir filesystem might have attributes disabled.
  _TMP_DIR = path.join(path.dirname(__file__), '.tmp')

  @classmethod
  def setUpClass(clazz):
    bfile_metadata_factory_registry.register_factory(bfile_metadata_factory_mime)

  @classmethod
  def tearDownClass(clazz):
    bfile_metadata_factory_registry.clear_all()
  
  def test_get_mime_type_jpeg(self):
    self.assertEqual( 'image/jpeg',
                      bfile_metadata.get_cached_metadata(self.jpg_file, 'bes', 'mime', 'mime_type', '1.0') )

  def xtest_get_mime_type_png(self):
    self.assertEqual( 'image/png', file_attributes_metadata.get_mime_type(self.png_file) )

  def xtest_get_media_type(self):
    self.assertEqual( 'image', file_attributes_metadata.get_media_type(self.jpg_file) )
    self.assertEqual( 'image', file_attributes_metadata.get_media_type(self.png_file) )
    self.assertEqual( 'video', file_attributes_metadata.get_media_type(self.mp4_file) )
    self.assertEqual( 'unknown', file_attributes_metadata.get_media_type(self.unknown_file) )
    
  def xtest_get_mime_type_change(self):
    tmp_file = self.make_temp_file(suffix = '.png')
    file_util.copy(self.png_file, tmp_file)
    self.assertEqual( 'image/png', file_attributes_metadata.get_mime_type(tmp_file) )
    with open(tmp_file, 'wb') as to_file:
      with open(self.jpg_file, 'rb') as from_file:
        to_file.write(from_file.read())
        to_file.flush()
        # for some reason on some linuxes the modification date does not change
        # when we clobber the png file with jpg content
        if host.is_linux():
          file_util.set_modification_date(tmp_file, datetime.now())
    self.assertEqual( 'image/jpeg', file_attributes_metadata.get_mime_type(tmp_file) )

  def xtest_get_mime_type_cached(self):
    tmp_file = self.make_temp_file(suffix = '.png')
    file_util.copy(self.png_file, tmp_file)
    self.assertEqual( 'image/png', file_attributes_metadata.get_mime_type(tmp_file, cached = True) )
    file_util.copy(self.jpg_file, tmp_file)
    if host.is_linux():
      file_util.set_modification_date(tmp_file, datetime.now())
    self.assertEqual( 'image/jpeg', file_attributes_metadata.get_mime_type(tmp_file, cached = True) )
    
    bfile_metadata_factory_registry.clear_all()

if __name__ == '__main__':
  unit_test.main()

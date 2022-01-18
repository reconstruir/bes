#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from datetime import datetime
from datetime import timedelta

from os import path

from bes.testing.unit_test import unit_test
from bes.fs.file_mime import file_mime
from bes.fs.file_util import file_util
from bes.fs.file_attributes_metadata import file_attributes_metadata
from bes.fs.file_attributes import file_attributes

from _bes_unit_test_common.unit_test_media import unit_test_media
from _bes_unit_test_common.unit_test_media_files import unit_test_media_files

class test_file_attributes_metadata(unit_test, unit_test_media_files):

  def test_get_bytes(self):
    tmp = self.make_temp_file(content = 'this is foo', suffix = '.txt')
    yesterday = datetime.now() - timedelta(days = 1)
    file_util.set_modification_date(tmp, yesterday)

    counter = 0
    def _value_maker1():
      nonlocal counter
      counter += 1
      return b'666'

    def _value_maker2():
      nonlocal counter
      counter += 1
      return b'667'
    
    self.assertEqual( 0, counter )
    self.assertEqual( b'666', file_attributes_metadata.get_bytes(tmp, 'foo', _value_maker1) )
    self.assertEqual( 1, counter )
    self.assertEqual( b'666', file_attributes_metadata.get_bytes(tmp, 'foo', _value_maker1) )
    self.assertEqual( 1, counter )
    mtime = file_util.get_modification_date(tmp)
    self.assertEqual( {
      '__bes_mtime_foo__': str(mtime.timestamp()).encode('utf-8'),
      'foo': b'666',
    }, file_attributes.get_all(tmp) )

    with open(tmp, 'a') as f:
      f.write(' more text')
      f.flush()

    self.assertEqual( 'this is foo more text', file_util.read(tmp, codec = 'utf-8') )

    self.assertEqual( b'667', file_attributes_metadata.get_bytes(tmp, 'foo', _value_maker2) )
    self.assertEqual( 2, counter )
    self.assertEqual( b'667', file_attributes_metadata.get_bytes(tmp, 'foo', _value_maker2) )
    self.assertEqual( 2, counter )

    new_mtime = file_util.get_modification_date(tmp)
    
    self.assertEqual( {
      '__bes_mtime_foo__': str(new_mtime.timestamp()).encode('utf-8'),
      'foo': b'667',
    }, file_attributes.get_all(tmp) )

  def test_get_mime_type_jpeg(self):
    self.assertEqual( 'image/jpeg', file_attributes_metadata.get_mime_type(self.jpg_file) )

  def test_get_mime_type_png(self):
    self.assertEqual( 'image/png', file_attributes_metadata.get_mime_type(self.png_file) )

  def test_get_media_type(self):
    self.assertEqual( 'image', file_attributes_metadata.get_media_type(self.jpg_file) )
    self.assertEqual( 'image', file_attributes_metadata.get_media_type(self.png_file) )
    self.assertEqual( 'video', file_attributes_metadata.get_media_type(self.mp4_file) )
    self.assertEqual( 'unknown', file_attributes_metadata.get_media_type(self.unknown_file) )
    
  def test_get_mime_type_change(self):
    tmp_file = self.make_temp_file(suffix = '.jpg')
    file_util.copy(self.png_file, tmp_file)
    self.assertEqual( 'image/png', file_attributes_metadata.get_mime_type(tmp_file) )
    with open(tmp_file, 'wb') as to_file:
      with open(self.jpg_file, 'rb') as from_file:
        to_file.write(from_file.read())
    self.assertEqual( 'image/jpeg', file_attributes_metadata.get_mime_type(tmp_file) )

  def test_get_mime_type_cached(self):
    tmp_file = self.make_temp_file(suffix = '.jpg')
    file_util.copy(self.png_file, tmp_file)
    self.assertEqual( 'image/png', file_attributes_metadata.get_mime_type_cached(tmp_file) )
    file_util.copy(self.jpg_file, tmp_file)
    self.assertEqual( 'image/jpeg', file_attributes_metadata.get_mime_type_cached(tmp_file) )
    
if __name__ == '__main__':
  unit_test.main()

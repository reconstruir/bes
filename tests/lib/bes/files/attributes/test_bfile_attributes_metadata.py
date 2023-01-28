#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from datetime import datetime
from datetime import timedelta

from os import path

from bes.files.attributes.bfile_attributes import bfile_attributes
from bes.files.attributes.bfile_attributes_metadata import bfile_attributes_metadata
from bes.fs.file_mime import file_mime
from bes.fs.file_util import file_util
from bes.fs.file_metadata_getter_base import file_metadata_getter_base
from bes.system.filesystem import filesystem
from bes.system.host import host
from bes.testing.unit_test import unit_test

from _bes_unit_test_common.unit_test_media import unit_test_media
from _bes_unit_test_common.unit_test_media_files import unit_test_media_files

class test_bfile_attributes_metadata(unit_test, unit_test_media_files):

  def test_get_bytes(self):
    tmp = self.make_temp_file(content = 'this is foo', suffix = '.txt')
    value = '666'.encode('utf-8')
    def _value_maker(f):
      return value
    self.assertEqual( value, bfile_attributes_metadata.get_bytes(tmp, 'foo', _value_maker) )
    self.assertEqual( [ '__bes_mtime_foo__', 'foo' ], bfile_attributes.keys(tmp) )
    self.assertEqual( '666', bfile_attributes.get_string(tmp, 'foo') )

  def test_get_bytes_none_value(self):
    tmp = self.make_temp_file(content = 'this is foo', suffix = '.txt')
    def _value_maker(f):
      return None
    self.assertEqual( None, bfile_attributes_metadata.get_bytes(tmp, 'foo', _value_maker) )
    self.assertEqual( [], bfile_attributes.keys(tmp) )
    
  def test_get_bytes_with_change(self):
    tmp = self.make_temp_file(content = 'this is foo', suffix = '.txt')
    yesterday = datetime.now() - timedelta(days = 1)
    file_util.set_modification_date(tmp, yesterday)

    counter = 0
    def _value_maker1(f):
      nonlocal counter
      counter += 1
      return b'666'

    def _value_maker2(f):
      nonlocal counter
      counter += 1
      return b'667'
    
    self.assertEqual( 0, counter )
    self.assertEqual( b'666', bfile_attributes_metadata.get_bytes(tmp, 'foo', _value_maker1) )
    self.assertEqual( 1, counter )
    self.assertEqual( b'666', bfile_attributes_metadata.get_bytes(tmp, 'foo', _value_maker1) )
    self.assertEqual( 1, counter )
    mtime = file_util.get_modification_date(tmp)
    self.assertEqual( {
      '__bes_mtime_foo__': str(mtime.timestamp()).encode('utf-8'),
      'foo': b'666',
    }, bfile_attributes.get_all(tmp) )

    with open(tmp, 'a') as f:
      f.write(' more text')
      f.flush()

    self.assertEqual( 'this is foo more text', file_util.read(tmp, codec = 'utf-8') )

    self.assertEqual( b'667', bfile_attributes_metadata.get_bytes(tmp, 'foo', _value_maker2) )
    self.assertEqual( 2, counter )
    self.assertEqual( b'667', bfile_attributes_metadata.get_bytes(tmp, 'foo', _value_maker2) )
    self.assertEqual( 2, counter )

    new_mtime = file_util.get_modification_date(tmp)
    
    self.assertEqual( {
      '__bes_mtime_foo__': str(new_mtime.timestamp()).encode('utf-8'),
      'foo': b'667',
    }, bfile_attributes.get_all(tmp) )

  def test_get_mime_type_jpeg(self):
    self.assertEqual( 'image/jpeg', bfile_attributes_metadata.get_mime_type(self.jpg_file) )

  def test_get_mime_type_png(self):
    self.assertEqual( 'image/png', bfile_attributes_metadata.get_mime_type(self.png_file) )

  def test_get_media_type(self):
    self.assertEqual( 'image', bfile_attributes_metadata.get_media_type(self.jpg_file) )
    self.assertEqual( 'image', bfile_attributes_metadata.get_media_type(self.png_file) )
    self.assertEqual( 'video', bfile_attributes_metadata.get_media_type(self.mp4_file) )
    self.assertEqual( 'unknown', bfile_attributes_metadata.get_media_type(self.unknown_file) )
    
  def test_get_mime_type_change(self):
    tmp_file = self.make_temp_file(suffix = '.png')
    file_util.copy(self.png_file, tmp_file)
    self.assertEqual( 'image/png', bfile_attributes_metadata.get_mime_type(tmp_file) )
    with open(tmp_file, 'wb') as to_file:
      with open(self.jpg_file, 'rb') as from_file:
        to_file.write(from_file.read())
        to_file.flush()
        # for some reason on some linuxes the modification date does not change
        # when we clobber the png file with jpg content
        if host.is_linux():
          file_util.set_modification_date(tmp_file, datetime.now())
    self.assertEqual( 'image/jpeg', bfile_attributes_metadata.get_mime_type(tmp_file) )

  def test_get_mime_type_cached(self):
    tmp_file = self.make_temp_file(suffix = '.png')
    file_util.copy(self.png_file, tmp_file)
    self.assertEqual( 'image/png', bfile_attributes_metadata.get_mime_type(tmp_file, cached = True) )
    file_util.copy(self.jpg_file, tmp_file)
    if host.is_linux():
      file_util.set_modification_date(tmp_file, datetime.now())
    self.assertEqual( 'image/jpeg', bfile_attributes_metadata.get_mime_type(tmp_file, cached = True) )

  def test_register_getter(self):
    class _test_getter_file_size(file_metadata_getter_base):

      @classmethod
      #@abstractmethod
      def name(clazz):
        return 'my_file_size'

      #@abstractmethod
      def get_value(self, manager, filename):
        value = 'kiwi:' + path.basename(filename)
        return value.encode('utf-8')

      #@abstractmethod
      def decode_value(self, value):
        return value.decode('utf-8')

    bfile_attributes_metadata.register_getter(_test_getter_file_size)
    tmp_file = self.make_temp_file(suffix = '.png')
    file_util.copy(self.png_file, tmp_file)
    self.assertEqual( 'kiwi:' + path.basename(tmp_file), bfile_attributes_metadata.get_value(tmp_file,
                                                                                            'my_file_size',
                                                                                            fallback = False) )

  def test_remove_value(self):
    tmp = self.make_temp_file(content = 'this is foo', suffix = '.txt')
    value = '666'.encode('utf-8')
    def _value_maker(f):
      return value
    self.assertEqual( value, bfile_attributes_metadata.get_bytes(tmp, 'foo', _value_maker) )
    self.assertEqual( [ '__bes_mtime_foo__', 'foo' ], bfile_attributes.keys(tmp) )
    self.assertEqual( '666', bfile_attributes.get_string(tmp, 'foo') )
    
if __name__ == '__main__':
  unit_test.main()

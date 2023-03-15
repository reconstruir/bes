#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from datetime import datetime
from datetime import timedelta

import os
from os import path

from bes.files.bfile_permission_error import bfile_permission_error
from bes.files.bfile_entry import bfile_entry
from bes.files.bfile_checksum import bfile_checksum
from bes.files.bfile_symlink import bfile_symlink
from bes.system.filesystem import filesystem
from bes.system.check import check
from bes.testing.unit_test import unit_test

from _bes_unit_test_common.unit_test_media import unit_test_media
from _bes_unit_test_common.unit_test_media_files import unit_test_media_files

class test_bfile_entry(unit_test, unit_test_media_files):
  
  def _make_test_entry(self, *args, **kargs):
    tmp = self.make_temp_file(*args, **kargs)
    return bfile_entry(tmp)

  def _make_test_entry_dir(self, *args, **kargs):
    tmp = self.make_temp_dir(*args, **kargs)
    return bfile_entry(tmp)

  def _make_test_entry_link(self, *args, **kargs):
    tmp1 = self.make_temp_file(*args, **kargs)
    tmp2 = self.make_temp_file(suffix = '-two')
    filesystem.remove(tmp2)
    os.symlink(tmp1, tmp2)
    return bfile_entry(tmp2)

  def _make_tmp_dir(self):
    return self.make_temp_dir(prefix = 'test_bfile_entry_', suffix = '.dir')

  def _make_test_entry_root_dir(self, root_dir, fragment, basename):
    filename = path.join(root_dir, fragment, basename)
    return bfile_entry(filename, root_dir = root_dir)
  
  def test_exits_true(self):
    self.assertEqual( True, self._make_test_entry().exists )

  def test_exits_false(self):
    e = self._make_test_entry()
    self.assertEqual( True, e.exists )
    filesystem.remove(e.filename)
    self.assertEqual( False, e.exists )

  def test_access(self):
    self.assertEqual( ( True, True, True, False ), self._make_test_entry().access )

  def test_is_file(self):
    self.assertEqual( True, self._make_test_entry().is_file )
    self.assertEqual( 'file', self._make_test_entry().file_type )

  def test_is_dir(self):
    self.assertEqual( True, self._make_test_entry_dir().is_dir )
    self.assertEqual( 'dir', self._make_test_entry_dir().file_type )

  def test_is_link(self):
    self.assertEqual( True, self._make_test_entry_link().is_link )
    self.assertEqual( 'link', self._make_test_entry_link().file_type )
    
  def test_size(self):
    self.assertEqual( 4, self._make_test_entry(content = 'kiwi').size )

  def test_extension(self):
    self.assertEqual( 'kiwi', self._make_test_entry(suffix = '.kiwi').extension )
    
  def test_modification_date_get(self):
    e = self._make_test_entry()
    self.assertEqual( datetime.fromtimestamp(path.getmtime(e.filename)), e.modification_date )

  def test_modification_date_set(self):
    e = self._make_test_entry()
    d = datetime(year = 2000, month = 1, day = 1, hour = 1, second = 1)
    e.modification_date = d
    self.assertEqual( d, e.modification_date )

  def test_modification_date_timestamp(self):
    e = self._make_test_entry()
    e.modification_date = datetime(year = 2000, month = 1, day = 1, hour = 1, second = 1)
    self.assertEqual( '2000-01-01-01-00-01', e.modification_date_timestamp )

  def test_attributes_has_key_false(self):
    tmp = self._make_test_entry(dir = __file__, content = 'foo')
    self.assertFalse( tmp.attributes.has_key('foo') )
  
  def test_attributes_has_key_true(self):
    tmp = self._make_test_entry(dir = __file__, content = 'foo')
    tmp.attributes.set_bytes('foo', 'hi'.encode('utf-8'))
    self.assertTrue( tmp.attributes.has_key('foo') )
    
  def test_attributes_get_bytes_never_set(self):
    tmp = self._make_test_entry(dir = __file__, content = 'foo')
    self.assertEqual( None, tmp.attributes.get_bytes('foo') )
  
  def test_attributes_set_bytes_get_bytes(self):
    tmp = self._make_test_entry(dir = __file__, content = 'foo')
    tmp.attributes.set_bytes('foo', 'hi'.encode('utf-8'))
    self.assertEqual( 'hi', tmp.attributes.get_bytes('foo').decode('utf-8') )
    tmp.attributes.set_bytes('bar', '99'.encode('utf-8'))
    self.assertEqual( '99', tmp.attributes.get_bytes('bar').decode('utf-8') )

  def test_attributes_empty_keys(self):
    tmp = self._make_test_entry(dir = __file__, content = 'foo')
    self.assertEqual( [], tmp.attributes.keys() )

  def test_attributes_keys(self):
    tmp = self._make_test_entry(dir = __file__, content = 'foo')
    tmp.attributes.set_bytes('foo', 'hi'.encode('utf-8'))
    tmp.attributes.set_bytes('bar', '99'.encode('utf-8'))
    self.assertEqual( [ 'bar', 'foo' ], tmp.attributes.keys() )
    
  def test_attributes_clear(self):
    tmp = self._make_test_entry(dir = __file__, content = 'foo')
    tmp.attributes.set_bytes('foo', 'hi'.encode('utf-8'))
    tmp.attributes.set_bytes('bar', '99'.encode('utf-8'))
    self.assertEqual( [ 'bar', 'foo' ], tmp.attributes.keys() )
    tmp.attributes.clear()
    self.assertEqual( [], tmp.attributes.keys() )

  def test_attributes_set_png_get_png(self):
    tmp = self._make_test_entry(dir = __file__, content = 'foo')
    data = unit_test_media.PNG_SMALLEST_POSSIBLE
    tmp.attributes.set_bytes('picture', data)
    self.assertEqual( data, tmp.attributes.get_bytes('picture') )

  def test_attributes_set_string_get_string(self):
    tmp = self._make_test_entry(dir = __file__, content = 'foo')
    tmp.attributes.set_string('foo', 'hi')
    self.assertEqual( 'hi', tmp.attributes.get_string('foo') )
      
  def test_attributes_set_date_get_date(self):
    tmp = self._make_test_entry(dir = __file__, content = 'foo')
    now = datetime.now()
    tmp.attributes.set_date('foo', now)
    self.assertEqual( now, tmp.attributes.get_date('foo') )

  def test_attributes_set_all_get_all(self):
    tmp = self._make_test_entry(dir = __file__, content = 'foo')
    d = {
      'foo': b'hi',
      'bar': b'666',
    }
    tmp.attributes.set_all(d)
    self.assertEqual( d, tmp.attributes.get_all() )

  def test_attributes_set_bool_get_bool(self):
    tmp = self._make_test_entry(dir = __file__, content = 'foo')
    tmp.attributes.set_bool('foo', True)
    tmp.attributes.set_bool('bar', False)
    self.assertEqual( True, tmp.attributes.get_bool('foo') )
    self.assertEqual( False, tmp.attributes.get_bool('bar') )
      
  def test_attributes_set_int_get_int(self):
    tmp = self._make_test_entry(dir = __file__, content = 'foo')
    tmp.attributes.set_int('foo', 666)
    tmp.attributes.set_int('bar', -1024)
    self.assertEqual( 666, tmp.attributes.get_int('foo') )
    self.assertEqual( -1024, tmp.attributes.get_int('bar') )
      
  def test_attributes_set_no_write_permission_unix(self):
    tmp = self._make_test_entry(dir = __file__, perm = 0o0400)
    with self.assertRaises(bfile_permission_error) as ctx:
      tmp.attributes.set_string('foo', 'hi')

  def test_attributes_remove_no_write_permission_unix(self):
    tmp = self._make_test_entry(dir = __file__, perm = 0o0400)
    with self.assertRaises(bfile_permission_error) as ctx:
      tmp.attributes.remove('foo')

  def test_attributes_clear_no_write_permission_unix(self):
    tmp = self._make_test_entry(dir = __file__, perm = 0o0400)
    with self.assertRaises(bfile_permission_error) as ctx:
      tmp.attributes.clear()

  def test_metadata_checksum_md5(self):
    tmp = self._make_test_entry(dir = __file__, content = 'this is kiwi')
    self.assertEqual( bfile_checksum.checksum(tmp.filename, 'md5'), tmp.checksum_md5 )
      
  def test_metadata_checksum_sha1(self):
    tmp = self._make_test_entry(dir = __file__, content = 'this is kiwi')
    self.assertEqual( bfile_checksum.checksum(tmp.filename, 'sha1'), tmp.checksum_sha1 )

  def test_metadata_checksum_sha256(self):
    tmp = self._make_test_entry(dir = __file__, content = 'this is kiwi')
    self.assertEqual( bfile_checksum.checksum(tmp.filename, 'sha256'), tmp.checksum_sha256 )

  def test_metadata_mime_type(self):
    tmp = self._make_test_entry(dir = __file__, content = unit_test_media.PNG_SMALLEST_POSSIBLE, suffix = '.png')
    self.assertEqual( 'image/png', tmp.mime_type )

  def test_metadata_media_type(self):
    tmp = self._make_test_entry(dir = __file__, content = unit_test_media.PNG_SMALLEST_POSSIBLE, suffix = '.png')
    self.assertEqual( 'image', tmp.media_type )
    self.assertEqual( True, tmp.is_image )

  def test_relative_filename(self):
    tmp_dir = self._make_tmp_dir()
    e = self._make_test_entry_root_dir(tmp_dir, 'stuff', 'fruits/kiwi.fruit')
    self.assert_filename_equal( 'stuff/fruits/kiwi.fruit', e.relative_filename )

  def test_filename_for_matcher(self):
    tmp_dir = self._make_tmp_dir()
    e = self._make_test_entry_root_dir(tmp_dir, 'stuff', 'fruits/Kiwi.fruit')
    self.assert_filename_equal( path.join(tmp_dir, 'stuff/fruits/Kiwi.fruit'),
                                e.filename_for_matcher('absolute', False) )
    self.assert_filename_equal( 'stuff/fruits/Kiwi.fruit',
                                e.filename_for_matcher('relative', False) )
    self.assert_filename_equal( 'Kiwi.fruit',
                                e.filename_for_matcher('basename', False) )
    self.assert_filename_equal( 'stuff/fruits/kiwi.fruit',
                                e.filename_for_matcher('relative', True) )
    
if __name__ == '__main__':
  unit_test.main()

#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from datetime import datetime
from datetime import timedelta

from os import path

from bes.files.bfile_permission_error import bfile_permission_error
from bes.files.bfile_entry import bfile_entry
from bes.system.filesystem import filesystem
from bes.system.check import check
from bes.testing.unit_test import unit_test

from _bes_unit_test_common.unit_test_media import unit_test_media
from _bes_unit_test_common.unit_test_media_files import unit_test_media_files

class test_bfile_entry(unit_test, unit_test_media_files):
  
  def F(self, *args, **kargs):
    tmp = self.make_temp_file(*args, **kargs)
    return bfile_entry(tmp)

  def D(self, *args, **kargs):
    tmp = self.make_temp_dir(*args, **kargs)
    return bfile_entry(tmp)
  
  def test_exits_true(self):
    self.assertEquals( True, self.F().exists )

  def test_exits_false(self):
    e = self.F()
    self.assertEquals( True, e.exists )
    filesystem.remove(e.filename)
    self.assertEquals( False, e.exists )

  def test_access(self):
    self.assertEquals( ( True, True, True, False ), self.F().access )

  def test_is_file(self):
    self.assertEquals( True, self.F().is_file )

  def test_is_dir(self):
    self.assertEquals( True, self.D().is_dir )

  def test_size(self):
    self.assertEquals( 4, self.F(content = 'kiwi').size )

  def test_extension(self):
    self.assertEquals( 'kiwi', self.F(suffix = '.kiwi').extension )
    
  def test_modification_date_get(self):
    e = self.F()
    self.assertEqual( datetime.fromtimestamp(path.getmtime(e.filename)), e.modification_date )

  def test_modification_date_set(self):
    e = self.F()
    d = datetime(year = 2000, month = 1, day = 1, hour = 1, second = 1)
    e.modification_date = d
    self.assertEqual( d, e.modification_date )

  def test_modification_date_timestamp(self):
    e = self.F()
    e.modification_date = datetime(year = 2000, month = 1, day = 1, hour = 1, second = 1)
    self.assertEqual( '2000-01-01-01-00-01', e.modification_date_timestamp )

  # Use a temporary directory in the same filesystem as the code to avoid the
  # issue that on some platforms the tmp dir filesystem might have attributes disabled.
  _TMP_DIR = path.join(path.dirname(__file__), '.tmp')
    
  def test_has_key_false(self):
    tmp = self.F(dir = self._TMP_DIR, content = 'foo')
    self.assertFalse( tmp.attr_has_key('foo') )
  
  def test_has_key_true(self):
    tmp = self.F(dir = self._TMP_DIR, content = 'foo')
    tmp.attr_set_bytes('foo', 'hi'.encode('utf-8'))
    self.assertTrue( tmp.attr_has_key('foo') )
    
  def test_get_bytes_never_set(self):
    tmp = self.F(dir = self._TMP_DIR, content = 'foo')
    self.assertEqual( None, tmp.attr_get_bytes('foo') )
  
  def test_set_bytes_get_bytes(self):
    tmp = self.F(dir = self._TMP_DIR, content = 'foo')
    tmp.attr_set_bytes('foo', 'hi'.encode('utf-8'))
    self.assertEqual( 'hi', tmp.attr_get_bytes('foo').decode('utf-8') )
    tmp.attr_set_bytes('bar', '99'.encode('utf-8'))
    self.assertEqual( '99', tmp.attr_get_bytes('bar').decode('utf-8') )

  def test_empty_keys(self):
    tmp = self.F(dir = self._TMP_DIR, content = 'foo')
    self.assertEqual( [], self._munge_attr_keys(tmp.attr_keys()) )

  def test_keys(self):
    tmp = self.F(dir = self._TMP_DIR, content = 'foo')
    tmp.attr_set_bytes('foo', 'hi'.encode('utf-8'))
    tmp.attr_set_bytes('bar', '99'.encode('utf-8'))
    self.assertEqual( [ 'bar', 'foo' ], self._munge_attr_keys(tmp.attr_keys()) )
    
  def test_clear(self):
    tmp = self.F(dir = self._TMP_DIR, content = 'foo')
    tmp.attr_set_bytes('foo', 'hi'.encode('utf-8'))
    tmp.attr_set_bytes('bar', '99'.encode('utf-8'))
    self.assertEqual( [ 'bar', 'foo' ], self._munge_attr_keys(tmp.attr_keys()) )
    tmp.attr_clear()
    self.assertEqual( [], self._munge_attr_keys(tmp.attr_keys()) )

  def test_set_png_get_png(self):
    tmp = self.F(dir = self._TMP_DIR, content = 'foo')
    data = unit_test_media.PNG_SMALLEST_POSSIBLE
    tmp.attr_set_bytes('picture', data)
    self.assertEqual( data, tmp.attr_get_bytes('picture') )

  def test_set_string_get_string(self):
    tmp = self.F(dir = self._TMP_DIR, content = 'foo')
    tmp.attr_set_string('foo', 'hi')
    self.assertEqual( 'hi', tmp.attr_get_string('foo') )
      
  def test_set_date_get_date(self):
    tmp = self.F(dir = self._TMP_DIR, content = 'foo')
    now = datetime.now()
    tmp.attr_set_date('foo', now)
    self.assertEqual( now, tmp.attr_get_date('foo') )

  def test_set_all_get_all(self):
    tmp = self.F(dir = self._TMP_DIR, content = 'foo')
    d = {
      'foo': b'hi',
      'bar': b'666',
    }
    tmp.attr_set_all(d)
    self.assertEqual( d, tmp.attr_get_all() )

  def test_set_bool_get_bool(self):
    tmp = self.F(dir = self._TMP_DIR, content = 'foo')
    tmp.attr_set_bool('foo', True)
    tmp.attr_set_bool('bar', False)
    self.assertEqual( True, tmp.attr_get_bool('foo') )
    self.assertEqual( False, tmp.attr_get_bool('bar') )
      
  def test_set_int_get_int(self):
    tmp = self.F(dir = self._TMP_DIR, content = 'foo')
    tmp.attr_set_int('foo', 666)
    tmp.attr_set_int('bar', -1024)
    self.assertEqual( 666, tmp.attr_get_int('foo') )
    self.assertEqual( -1024, tmp.attr_get_int('bar') )
      
  def test_set_no_write_permission_unix(self):
    tmp = self.F(dir = self._TMP_DIR, perm = 0o0400)
    with self.assertRaises(bfile_permission_error) as ctx:
      tmp.attr_set_string('foo', 'hi')

  def test_remove_no_write_permission_unix(self):
    tmp = self.F(dir = self._TMP_DIR, perm = 0o0400)
    with self.assertRaises(bfile_permission_error) as ctx:
      tmp.attr_remove('foo')

  def test_clear_no_write_permission_unix(self):
    tmp = self.F(dir = self._TMP_DIR, perm = 0o0400)
    with self.assertRaises(bfile_permission_error) as ctx:
      tmp.attr_clear()
        
  @classmethod
  def _munge_attr_keys(clazz, keys):
    'On some linux systems, there is an extra selinux key in many attr results'
    # FIXME: move this to the linux implementation and perhaps add a show system
    # attributes boolean somewhere
    check.check_list(keys)
    return [ key for key in keys if key != 'selinux' ]

if __name__ == '__main__':
  unit_test.main()

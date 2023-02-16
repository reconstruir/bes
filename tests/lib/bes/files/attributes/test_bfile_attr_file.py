#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from datetime import datetime

from bes.files.bfile_permission_error import bfile_permission_error
from bes.files.attributes.bfile_attr_file import bfile_attr_file
from bes.system.check import check
from bes.testing.unit_test import unit_test

from _bes_unit_test_common.unit_test_media import unit_test_media
from _bes_unit_test_common.unit_test_media_files import unit_test_media_files

class test_bfile_attr_file(unit_test, unit_test_media_files):

  def _make_test_entry(self, *args, **kargs):
    tmp = self.make_temp_file(dir = __file__, *args, **kargs)
    return bfile_attr_file(tmp)
  
  def test_has_key_false(self):
    tmp = self._make_test_entry(content = 'foo')
    self.assertFalse( tmp.has_key('foo') )
  
  def test_has_key_true(self):
    tmp = self._make_test_entry(content = 'foo')
    tmp.set_bytes('foo', 'hi'.encode('utf-8'))
    self.assertTrue( tmp.has_key('foo') )
    
  def test_get_bytes_never_set(self):
    tmp = self._make_test_entry(content = 'foo')
    self.assertEqual( None, tmp.get_bytes('foo') )
  
  def test_set_bytes_get_bytes(self):
    tmp = self._make_test_entry(content = 'foo')
    tmp.set_bytes('foo', 'hi'.encode('utf-8'))
    self.assertEqual( 'hi', tmp.get_bytes('foo').decode('utf-8') )
    tmp.set_bytes('bar', '99'.encode('utf-8'))
    self.assertEqual( '99', tmp.get_bytes('bar').decode('utf-8') )

  def test_empty_keys(self):
    tmp = self._make_test_entry(content = 'foo')
    self.assertEqual( [], tmp.keys() )

  def test_keys(self):
    tmp = self._make_test_entry(content = 'foo')
    tmp.set_bytes('foo', 'hi'.encode('utf-8'))
    tmp.set_bytes('bar', '99'.encode('utf-8'))
    self.assertEqual( [ 'bar', 'foo' ], tmp.keys() )
    
  def test_clear(self):
    tmp = self._make_test_entry(content = 'foo')
    tmp.set_bytes('foo', 'hi'.encode('utf-8'))
    tmp.set_bytes('bar', '99'.encode('utf-8'))
    self.assertEqual( [ 'bar', 'foo' ], tmp.keys() )
    tmp.clear()
    self.assertEqual( [], tmp.keys() )

  def test_set_png_get_png(self):
    tmp = self._make_test_entry(content = 'foo')
    data = unit_test_media.PNG_SMALLEST_POSSIBLE
    tmp.set_bytes('picture', data)
    self.assertEqual( data, tmp.get_bytes('picture') )

  def test_set_string_get_string(self):
    tmp = self._make_test_entry(content = 'foo')
    tmp.set_string('foo', 'hi')
    self.assertEqual( 'hi', tmp.get_string('foo') )
      
  def test_set_date_get_date(self):
    tmp = self._make_test_entry(content = 'foo')
    now = datetime.now()
    tmp.set_date('foo', now)
    self.assertEqual( now, tmp.get_date('foo') )

  def test_set_all_get_all(self):
    tmp = self._make_test_entry(content = 'foo')
    d = {
      'foo': b'hi',
      'bar': b'666',
    }
    tmp.set_all(d)
    self.assertEqual( d, tmp.get_all() )

  def test_set_bool_get_bool(self):
    tmp = self._make_test_entry(content = 'foo')
    tmp.set_bool('foo', True)
    tmp.set_bool('bar', False)
    self.assertEqual( True, tmp.get_bool('foo') )
    self.assertEqual( False, tmp.get_bool('bar') )
      
  def test_set_int_get_int(self):
    tmp = self._make_test_entry(content = 'foo')
    tmp.set_int('foo', 666)
    tmp.set_int('bar', -1024)
    self.assertEqual( 666, tmp.get_int('foo') )
    self.assertEqual( -1024, tmp.get_int('bar') )
      
  def test_set_no_write_permission_unix(self):
    tmp = self._make_test_entry(perm = 0o0400)
    with self.assertRaises(bfile_permission_error) as ctx:
      tmp.set_string('foo', 'hi')

  def test_remove_no_write_permission_unix(self):
    tmp = self._make_test_entry(perm = 0o0400)
    with self.assertRaises(bfile_permission_error) as ctx:
      tmp.remove('foo')

  def test_clear_no_write_permission_unix(self):
    tmp = self._make_test_entry(perm = 0o0400)
    with self.assertRaises(bfile_permission_error) as ctx:
      tmp.clear()
        
if __name__ == '__main__':
  unit_test.main()

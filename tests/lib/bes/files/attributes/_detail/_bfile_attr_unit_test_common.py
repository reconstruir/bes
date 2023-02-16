#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from datetime import datetime
import os.path as path

from bes.files.bfile_permission_error import bfile_permission_error
from bes.testing.unit_test import unit_test

from _bes_unit_test_common.unit_test_media import unit_test_media

def make_test_case(impl):
  
  class _bfile_attr_test_case(unit_test):

    def test_has_key_false(self):
      tmp = self.make_temp_file(dir = __file__, content = 'foo')
      self.assertFalse( impl.has_key(tmp, 'foo') )
  
    def test_has_key_true(self):
      tmp = self.make_temp_file(dir = __file__, content = 'foo')
      impl.set_bytes(tmp, 'foo', 'hi'.encode('utf-8'))
      self.assertTrue( impl.has_key(tmp, 'foo') )
    
    def test_get_bytes_never_set(self):
      tmp = self.make_temp_file(dir = __file__, content = 'foo')
      self.assertEqual( None, impl.get_bytes(tmp, 'foo') )
  
    def test_set_bytes_get_bytes(self):
      tmp = self.make_temp_file(dir = __file__, content = 'foo')
      impl.set_bytes(tmp, 'foo', 'hi'.encode('utf-8'))
      self.assertEqual( 'hi', impl.get_bytes(tmp, 'foo').decode('utf-8') )
      impl.set_bytes(tmp, 'bar', '99'.encode('utf-8'))
      self.assertEqual( '99', impl.get_bytes(tmp, 'bar').decode('utf-8') )

    def test_empty_keys(self):
      tmp = self.make_temp_file(dir = __file__, content = 'foo')
      self.assertEqual( [], self._munge_attr_keys(impl.keys(tmp)) )

    def test_keys(self):
      tmp = self.make_temp_file(dir = __file__, content = 'foo')
      impl.set_bytes(tmp, 'foo', 'hi'.encode('utf-8'))
      impl.set_bytes(tmp, 'bar', '99'.encode('utf-8'))
      self.assertEqual( [ 'bar', 'foo' ], self._munge_attr_keys(impl.keys(tmp)) )
    
    def test_clear(self):
      tmp = self.make_temp_file(dir = __file__, content = 'foo')
      impl.set_bytes(tmp, 'foo', 'hi'.encode('utf-8'))
      impl.set_bytes(tmp, 'bar', '99'.encode('utf-8'))
      self.assertEqual( [ 'bar', 'foo' ], self._munge_attr_keys(impl.keys(tmp)) )
      impl.clear(tmp)
      self.assertEqual( [], self._munge_attr_keys(impl.keys(tmp)) )

    def test_set_png_get_png(self):
      tmp = self.make_temp_file(dir = __file__, content = 'foo')
      data = unit_test_media.PNG_SMALLEST_POSSIBLE
      impl.set_bytes(tmp, 'picture', data)
      self.assertEqual( data, impl.get_bytes(tmp, 'picture') )

    def test_set_string_get_string(self):
      tmp = self.make_temp_file(dir = __file__, content = 'foo')
      impl.set_string(tmp, 'foo', 'hi')
      self.assertEqual( 'hi', impl.get_string(tmp, 'foo') )
      
    def test_set_date_get_date(self):
      tmp = self.make_temp_file(dir = __file__, content = 'foo')
      now = datetime.now()
      impl.set_date(tmp, 'foo', now)
      self.assertEqual( now, impl.get_date(tmp, 'foo') )

    def test_set_all_get_all(self):
      tmp = self.make_temp_file(dir = __file__, content = 'foo')
      d = {
        'foo': b'hi',
        'bar': b'666',
      }
      impl.set_all(tmp, d)
      self.assertEqual( d, impl.get_all(tmp) )

    def test_set_bool_get_bool(self):
      tmp = self.make_temp_file(dir = __file__, content = 'foo')
      impl.set_bool(tmp, 'foo', True)
      impl.set_bool(tmp, 'bar', False)
      self.assertEqual( True, impl.get_bool(tmp, 'foo') )
      self.assertEqual( False, impl.get_bool(tmp, 'bar') )
      
    def test_set_int_get_int(self):
      tmp = self.make_temp_file(dir = __file__, content = 'foo')
      impl.set_int(tmp, 'foo', 666)
      impl.set_int(tmp, 'bar', -1024)
      self.assertEqual( 666, impl.get_int(tmp, 'foo') )
      self.assertEqual( -1024, impl.get_int(tmp, 'bar') )
      
    def test_set_no_write_permission_unix(self):
      tmp = self.make_temp_file(dir = __file__, content = 'foo', perm = 0o0400)
      with self.assertRaises(bfile_permission_error) as ctx:
        impl.set_string(tmp, 'foo', 'hi')

    def test_remove_no_write_permission_unix(self):
      tmp = self.make_temp_file(dir = __file__, content = 'foo', perm = 0o0400)
      with self.assertRaises(bfile_permission_error) as ctx:
        impl.remove(tmp, 'foo')

    def test_clear_no_write_permission_unix(self):
      tmp = self.make_temp_file(dir = __file__, content = 'foo', perm = 0o0400)
      with self.assertRaises(bfile_permission_error) as ctx:
        impl.clear(tmp)

    @classmethod
    def _munge_attr_keys(clazz, keys):
      'On some linux systems, there is an extra selinux key in many attr results'
      # FIXME: move this to the linux implementation and perhaps add a show system
      # attributes boolean somewhere
      assert isinstance(keys, list)
      return [ key for key in keys if key != 'selinux' ]
      
  return _bfile_attr_test_case

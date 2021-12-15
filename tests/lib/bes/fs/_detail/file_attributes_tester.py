#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from datetime import datetime
import os.path as path

from bes.fs.file_symlink import file_symlink
from bes.fs.file_attributes_error import file_attributes_permission_error
from bes.testing.unit_test import unit_test
from bes.testing.unit_test_function_skip import unit_test_function_skip

from _bes_unit_test_common.unit_test_media import unit_test_media

def make_test_case(impl):
  
  class _file_attributes_test_case(unit_test):

    def test_has_key_false(self):
      tmp = self._make_temp_file('this is foo\n')
      self.assertFalse( impl.has_key(tmp, 'foo') )
  
    def test_has_key_true(self):
      tmp = self._make_temp_file('this is foo\n')
      impl.set_bytes(tmp, 'foo', 'hi'.encode('utf-8'))
      self.assertTrue( impl.has_key(tmp, 'foo') )
    
    def test_get_bytes_never_set(self):
      tmp = self._make_temp_file('this is foo\n')
      self.assertEqual( None, impl.get_bytes(tmp, 'foo') )
  
    def test_set_bytes_get_bytes(self):
      tmp = self._make_temp_file('this is foo\n')
      impl.set_bytes(tmp, 'foo', 'hi'.encode('utf-8'))
      self.assertEqual( 'hi', impl.get_bytes(tmp, 'foo').decode('utf-8') )
      impl.set_bytes(tmp, 'bar', '99'.encode('utf-8'))
      self.assertEqual( '99', impl.get_bytes(tmp, 'bar').decode('utf-8') )

    def test_empty_keys(self):
      tmp = self._make_temp_file('this is foo\n')
      self.assertEqual( [], self._munge_attr_keys(impl.keys(tmp)) )

    def test_keys(self):
      tmp = self._make_temp_file('this is foo\n')
      impl.set_bytes(tmp, 'foo', 'hi'.encode('utf-8'))
      impl.set_bytes(tmp, 'bar', '99'.encode('utf-8'))
      self.assertEqual( [ 'bar', 'foo' ], self._munge_attr_keys(impl.keys(tmp)) )
    
    def test_clear(self):
      tmp = self._make_temp_file('this is foo\n')
      impl.set_bytes(tmp, 'foo', 'hi'.encode('utf-8'))
      impl.set_bytes(tmp, 'bar', '99'.encode('utf-8'))
      self.assertEqual( [ 'bar', 'foo' ], self._munge_attr_keys(impl.keys(tmp)) )
      impl.clear(tmp)
      self.assertEqual( [], self._munge_attr_keys(impl.keys(tmp)) )

    def test_set_png_get_png(self):
      tmp = self._make_temp_file('this is foo\n')
      data = unit_test_media.PNG_SMALLEST_POSSIBLE
      impl.set_bytes(tmp, 'picture', data)
      self.assertEqual( data, impl.get_bytes(tmp, 'picture') )

    def test_set_string_get_string(self):
      tmp = self._make_temp_file('this is foo\n')
      impl.set_string(tmp, 'foo', 'hi')
      self.assertEqual( 'hi', impl.get_string(tmp, 'foo') )
      
    def test_set_date_get_date(self):
      tmp = self._make_temp_file('this is foo\n')
      now = datetime.now()
      impl.set_date(tmp, 'foo', now)
      self.assertEqual( now, impl.get_date(tmp, 'foo') )

    def test_set_all_get_all(self):
      tmp = self._make_temp_file('this is foo\n')
      d = {
        'foo': b'hi',
        'bar': b'666',
      }
      impl.set_all(tmp, d)
      self.assertEqual( d, impl.get_all(tmp) )

    @unit_test_function_skip.skip_if_not_unix()
    def test_set_no_permission_unix(self):
      exe = file_symlink.resolve('/bin/sh')
      with self.assertRaises(file_attributes_permission_error) as ctx:
        impl.set_string(exe, 'foo', 'hi')
      
    @classmethod
    def _munge_attr_keys(clazz, keys):
      'On some linux systems, there is an extra selinux key in many attr results'
      # FIXME: move this to the linux implementation and perhaps add a show system
      # attributes boolean somewhere
      assert isinstance(keys, list)
      return [ key for key in keys if key != 'selinux' ]

    def _make_temp_file(self, content):
      # Use a temporary directory in the same filesystem as the code to avoid the
      # issue that on some platforms the tmp dir filesystem might have attributes disabled.
      tmp_dir = path.join(path.dirname(__file__), '.tmp')
      return self.make_temp_file(content = content, dir = tmp_dir, suffix = '.txt')

  return _file_attributes_test_case

#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from datetime import datetime
import os.path as path
import stat

from bes.fs.file_attributes_error import file_attributes_permission_error
from bes.fs.file_symlink import file_symlink
from bes.system.host import host
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

    def test_set_bool_get_bool(self):
      tmp = self._make_temp_file('this is foo\n')
      impl.set_bool(tmp, 'foo', True)
      impl.set_bool(tmp, 'bar', False)
      self.assertEqual( True, impl.get_bool(tmp, 'foo') )
      self.assertEqual( False, impl.get_bool(tmp, 'bar') )
      
    def test_set_int_get_int(self):
      tmp = self._make_temp_file('this is foo\n')
      impl.set_int(tmp, 'foo', 666)
      impl.set_int(tmp, 'bar', -1024)
      self.assertEqual( 666, impl.get_int(tmp, 'foo') )
      self.assertEqual( -1024, impl.get_int(tmp, 'bar') )
      
    @unit_test_function_skip.skip_if_not_unix()
    def test_set_no_write_permission_unix(self):
      tmp = self._make_read_only_temp_file()
      with self.assertRaises(file_attributes_permission_error) as ctx:
        print('impl={}'.format(impl))
        impl.set_string(tmp, 'foo', 'hi')

    @unit_test_function_skip.skip_if_not_unix()
    def xtest_remove_no_write_permission_unix(self):
      tmp = self._make_read_only_temp_file()
      with self.assertRaises(file_attributes_permission_error) as ctx:
        impl.remove(tmp, 'foo')

    @unit_test_function_skip.skip_if_not_unix()
    def xtest_clear_no_write_permission_unix(self):
      tmp = self._make_read_only_temp_file()
      with self.assertRaises(file_attributes_permission_error) as ctx:
        impl.clear(tmp)
        
    def _make_read_only_temp_file(self):
      from bes.fs.file_util import file_util
      tmp = self._make_temp_file('this is foo\n')
      print('B4: tmp={} mode={}'.format(tmp, file_util.mode(tmp)))
      import os
#      os.chmod(tmp, stat.S_IREAD)
      os.chmod(tmp, 0o0400)
      print('AF: tmp={} mode={}'.format(tmp, file_util.mode(tmp)))
      return tmp
      if host.is_unix():
        return file_symlink.resolve('/bin/sh')
      elif host.is_windows():
        return r'C:\Windows\System32\cmd.exe'
      else:
        host.raise_unsupported_system()
        
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

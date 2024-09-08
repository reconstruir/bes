#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from datetime import datetime
from datetime import timedelta
import os.path as path

from bes.files.bf_permission_error import bf_permission_error
from bes.files.bf_date import bf_date

from bes.testing.unit_test import unit_test

from _bes_unit_test_common.unit_test_media import unit_test_media

from _bes_unit_test_common.files.attr2.fruits_factory import fruits_factory

def make_test_case(impl):
  class _bf_attr2_test_case(unit_test):

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
      self.assertEqual( [], impl.keys(tmp) )

    def test_keys(self):
      tmp = self.make_temp_file(dir = __file__, content = 'foo')
      impl.set_bytes(tmp, 'foo', 'hi'.encode('utf-8'))
      impl.set_bytes(tmp, 'bar', '99'.encode('utf-8'))
      self.assertEqual( [ 'bar', 'foo' ], impl.keys(tmp) )
    
    def test_clear(self):
      tmp = self.make_temp_file(dir = __file__, content = 'foo')
      impl.set_bytes(tmp, 'foo', 'hi'.encode('utf-8'))
      impl.set_bytes(tmp, 'bar', '99'.encode('utf-8'))
      self.assertEqual( [ 'bar', 'foo' ], impl.keys(tmp) )
      impl.clear(tmp)
      self.assertEqual( [], impl.keys(tmp) )

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
      with self.assertRaises(bf_permission_error) as ctx:
        impl.set_string(tmp, 'foo', 'hi')

    def test_remove_no_write_permission_unix(self):
      tmp = self.make_temp_file(dir = __file__, content = 'foo', perm = 0o0400)
      with self.assertRaises(bf_permission_error) as ctx:
        impl.remove(tmp, 'foo')

    def test_clear_no_write_permission_unix(self):
      tmp = self.make_temp_file(dir = __file__, content = 'foo', perm = 0o0400)
      with self.assertRaises(bf_permission_error) as ctx:
        impl.clear(tmp)

    def test_get_value_int(self):
      tmp = self.make_temp_file(dir = __file__, content = 'foo')
      self.assertEqual( None, impl.get_value(tmp, 'acme/fruit/kiwi/1.0') )
      impl.set_int(tmp, 'acme/fruit/kiwi/1.0', 666)
      self.assertEqual( 666, impl.get_value(tmp, 'acme/fruit/kiwi/1.0') )

    def test_get_value_float(self):
      tmp = self.make_temp_file(dir = __file__, content = 'foo')
      self.assertEqual( None, impl.get_value(tmp, 'acme/fruit/cherry/2.0') )
      impl.set_float(tmp, 'acme/fruit/cherry/2.0', 42.3)
      self.assertEqual( 42.3, impl.get_value(tmp, 'acme/fruit/cherry/2.0') )

    def test_get_value_date(self):
      tmp = self.make_temp_file(dir = __file__, content = 'foo')
      self.assertEqual( None, impl.get_value(tmp, 'acme/fruit/birthday/1.0') )
      now = datetime.now()
      impl.set_date(tmp, 'acme/fruit/birthday/1.0', now)
      self.assertEqual( now, impl.get_value(tmp, 'acme/fruit/birthday/1.0') )

    def test_get_value_with_old_keys(self):
      tmp = self.make_temp_file(dir = __file__, content = 'foo')
      self.assertEqual( False, impl.has_key(tmp, 'acme/fruit/is_favorite/1.0') )
      impl.set_bool(tmp, 'old_is_favorite1', True)
      self.assertEqual( True, impl.get_value(tmp, 'acme/fruit/is_favorite/1.0') )
      self.assertEqual( True, impl.has_key(tmp, 'acme/fruit/is_favorite/1.0') )
      impl.set_bool(tmp, 'old_is_favorite1', False)
      self.assertEqual( True, impl.get_value(tmp, 'acme/fruit/is_favorite/1.0') )

    def test_get_cached_bytes(self):
      tmp = self.make_temp_file(dir = __file__, content = 'foo')
      value = '666'.encode('utf-8')
      def _value_maker(f):
        return value
      self.assertEqual( value, impl.get_cached_bytes(tmp, 'foo', _value_maker) )
      self.assertEqual( [ '__bes_mtime_foo__', 'foo' ], impl.keys(tmp) )
      self.assertEqual( '666', impl.get_string(tmp, 'foo') )

    def test_get_cached_bytes_with_change(self):
      tmp = self.make_temp_file(dir = __file__, content = 'this is foo', suffix = '.txt')
      yesterday = datetime.now() - timedelta(days = 1)
      bf_date.set_modification_date(tmp, yesterday)

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
      self.assertEqual( b'666', impl.get_cached_bytes(tmp, 'foo', _value_maker1) )
      self.assertEqual( 1, counter )
      self.assertEqual( b'666', impl.get_cached_bytes(tmp, 'foo', _value_maker1) )
      self.assertEqual( 1, counter )
      mtime = bf_date.get_modification_date(tmp)
      self.assertEqual( {
        '__bes_mtime_foo__': str(mtime.timestamp()).encode('utf-8'),
        'foo': b'666',
      }, impl.get_all(tmp) )

      with open(tmp, 'a') as f:
        f.write(' more text')
        f.flush()

      with open(tmp, 'r') as f:
        tmp_content = f.read()
        self.assertEqual( 'this is foo more text', tmp_content )

      self.assertEqual( b'667', impl.get_cached_bytes(tmp, 'foo', _value_maker2) )
      self.assertEqual( 2, counter )
      self.assertEqual( b'667', impl.get_cached_bytes(tmp, 'foo', _value_maker2) )
      self.assertEqual( 2, counter )
  
      new_mtime = bf_date.get_modification_date(tmp)
    
      self.assertEqual( {
        '__bes_mtime_foo__': str(new_mtime.timestamp()).encode('utf-8'),
        'foo': b'667',
      }, impl.get_all(tmp) )
      
  return _bf_attr2_test_case

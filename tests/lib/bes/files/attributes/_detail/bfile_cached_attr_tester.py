#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os

from datetime import datetime
from datetime import timedelta
import os.path as path

from bes.files.bfile_date import bfile_date
from bes.files.attributes.bfile_attr_factory_base import bfile_attr_factory_base
from bes.files.attributes.bfile_cached_attr import bfile_cached_attr
from bes.files.attributes.bfile_attr_handler import bfile_attr_handler
from bes.testing.unit_test import unit_test

from _bes_unit_test_common.unit_test_media import unit_test_media

def make_test_case(impl):
  
  class _bfile_cached_attr_test_case(unit_test):

    # Use a temporary directory in the same filesystem as the code to avoid the
    # issue that on some platforms the tmp dir filesystem might have attributes disabled.
    _TMP_DIR = path.join(path.dirname(__file__), '.tmp')
    
    def test_get_cached_bytes(self):
      tmp = self.make_temp_file(dir = self._TMP_DIR, content = 'foo')
      value = '666'.encode('utf-8')
      def _value_maker(f):
        return value
      self.assertEqual( value, impl.get_cached_bytes(tmp, 'foo', _value_maker) )
      self.assertEqual( [ '__bes_mtime_foo__', 'foo' ], impl.keys(tmp) )
      self.assertEqual( '666', impl.get_string(tmp, 'foo') )

    def test_get_cached_bytes_with_change(self):
      tmp = self.make_temp_file(content = 'this is foo', suffix = '.txt')
      yesterday = datetime.now() - timedelta(days = 1)
      bfile_date.set_modification_date(tmp, yesterday)

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
      mtime = bfile_date.get_modification_date(tmp)
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
  
      new_mtime = bfile_date.get_modification_date(tmp)
    
      self.assertEqual( {
        '__bes_mtime_foo__': str(new_mtime.timestamp()).encode('utf-8'),
        'foo': b'667',
      }, impl. get_all(tmp) )

    def test_register_attr_factory(self):
      class _test_fruits_factory(bfile_attr_factory_base):
      
        @classmethod
        #@abstractmethod
        def handlers(clazz):
          return [
            ( 'fruit', 'kiwi', '1.0', clazz._get_kiwi_1_0, clazz._decode_kiwi_1_0, False ),
            ( 'fruit', 'cherry', '2.0', clazz._get_cherry_2_0, clazz._decode_cherry_2_0, False ),
          ]

        @classmethod
        def _get_kiwi_1_0(clazz, filename):
          return os.stat(filename).st_size

        @classmethod
        def _decode_kiwi_1_0(clazz, value):
          return clazz.decode_int(value)
        
        @classmethod
        def _get_cherry_2_0(clazz, filename):
          return os.stat(filename).st_size / 2.0

        @classmethod
        def _decode_cherry_2_0(clazz, value):
          return clazz.decode_float(value)
        
      bfile_cached_attr.register_attr_factory(_test_fruits_factory)
      tmp = self.make_temp_file(dir = self._TMP_DIR, content = 'foo')
      
  return _bfile_cached_attr_test_case

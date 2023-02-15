#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os

import os.path as path

from bes.files.attributes.bfile_metadata_factory_base import bfile_metadata_factory_base
from bes.files.attributes.bfile_metadata_factory_registry import bfile_metadata_factory_registry
from bes.files.bfile_date import bfile_date
from bes.testing.unit_test import unit_test

from _bes_unit_test_common.unit_test_media import unit_test_media

def make_test_case(impl):
  
  class _bfile_metadata_test_case(unit_test):

    # Use a temporary directory in the same filesystem as the code to avoid the
    # issue that on some platforms the tmp dir filesystem might have attributes disabled.
    _TMP_DIR = path.join(path.dirname(__file__), '.tmp')
    
    def test_get_cached_metadata(self):
      class _test_fruits_factory(bfile_metadata_factory_base):
      
        @classmethod
        #@abstractmethod
        def handlers(clazz):
          return [
            ( 'acme', 'fruit', 'kiwi', '1.0', clazz._get_kiwi_1_0, clazz._decode_kiwi_1_0, False ),
            ( 'acme', 'fruit', 'cherry', '2.0', clazz._get_cherry_2_0, clazz._decode_cherry_2_0, False ),
          ]

        _kiwi_1_0_count = 0
        @classmethod
        def _get_kiwi_1_0(clazz, filename):
          clazz._kiwi_1_0_count += 1
          return clazz.encode_int(os.stat(filename).st_size)

        @classmethod
        def _decode_kiwi_1_0(clazz, value):
          return clazz.decode_int(value)
        
        _cherry_2_0_count = 0
        @classmethod
        def _get_cherry_2_0(clazz, filename):
          clazz._cherry_2_0_count += 1
          return clazz.encode_float(os.stat(filename).st_size / 2.0)

        @classmethod
        def _decode_cherry_2_0(clazz, value):
          return clazz.decode_float(value)
        
      bfile_metadata_factory_registry.register_factory(_test_fruits_factory)
      tmp = self.make_temp_file(dir = self._TMP_DIR, content = b'12345', suffix = '.data')

      self.assertEqual( 0, _test_fruits_factory._kiwi_1_0_count )
      self.assertEqual( 5, impl.get_cached_metadata(tmp, 'acme', 'fruit', 'kiwi', '1.0') )
      self.assertEqual( 1, _test_fruits_factory._kiwi_1_0_count )
      self.assertEqual( 5, impl.get_cached_metadata(tmp, 'acme', 'fruit', 'kiwi', '1.0') )
      self.assertEqual( 1, _test_fruits_factory._kiwi_1_0_count )
      kiwi_mtime = bfile_date.get_modification_date(tmp)

      self.assertEqual( 0, _test_fruits_factory._cherry_2_0_count )
      self.assertEqual( 2.5, impl.get_cached_metadata(tmp, 'acme', 'fruit', 'cherry', '2.0') )
      self.assertEqual( 1, _test_fruits_factory._cherry_2_0_count )
      self.assertEqual( 2.5, impl.get_cached_metadata(tmp, 'acme', 'fruit', 'cherry', '2.0') )
      self.assertEqual( 1, _test_fruits_factory._cherry_2_0_count )
      cherry_mtime = bfile_date.get_modification_date(tmp)

      self.assertEqual( {
        '__bes_mtime_acme/fruit/cherry/2.0__': str(cherry_mtime.timestamp()).encode('utf-8'),
        '__bes_mtime_acme/fruit/kiwi/1.0__': str(kiwi_mtime.timestamp()).encode('utf-8'),
        'acme/fruit/cherry/2.0': b'2.5',
        'acme/fruit/kiwi/1.0': b'5',
      }, impl.get_all(tmp) )
      
      with open(tmp, 'wb') as f:
        f.write(b'1234567890')
        f.flush()

      self.assertEqual( 1, _test_fruits_factory._kiwi_1_0_count )
      self.assertEqual( 10, impl.get_cached_metadata(tmp, 'acme', 'fruit', 'kiwi', '1.0') )
      self.assertEqual( 2, _test_fruits_factory._kiwi_1_0_count )
      self.assertEqual( 10, impl.get_cached_metadata(tmp, 'acme', 'fruit', 'kiwi', '1.0') )
      self.assertEqual( 2, _test_fruits_factory._kiwi_1_0_count )
      kiwi_mtime = bfile_date.get_modification_date(tmp)

      self.assertEqual( {
        '__bes_mtime_acme/fruit/cherry/2.0__': str(cherry_mtime.timestamp()).encode('utf-8'),
        '__bes_mtime_acme/fruit/kiwi/1.0__': str(kiwi_mtime.timestamp()).encode('utf-8'),
        'acme/fruit/cherry/2.0': b'2.5',
        'acme/fruit/kiwi/1.0': b'10',
      }, impl.get_all(tmp) )
      
      with open(tmp, 'wb') as f:
        f.write(b'12')
        f.flush()
      
      self.assertEqual( 1, _test_fruits_factory._cherry_2_0_count )
      self.assertEqual( 1, impl.get_cached_metadata(tmp, 'acme', 'fruit', 'cherry', '2.0') )
      self.assertEqual( 2, _test_fruits_factory._cherry_2_0_count )
      self.assertEqual( 1, impl.get_cached_metadata(tmp, 'acme', 'fruit', 'cherry', '2.0') )
      self.assertEqual( 2, _test_fruits_factory._cherry_2_0_count )
      cherry_mtime = bfile_date.get_modification_date(tmp)

      self.assertEqual( {
        '__bes_mtime_acme/fruit/cherry/2.0__': str(cherry_mtime.timestamp()).encode('utf-8'),
        '__bes_mtime_acme/fruit/kiwi/1.0__': str(kiwi_mtime.timestamp()).encode('utf-8'),
        'acme/fruit/cherry/2.0': b'1.0',
        'acme/fruit/kiwi/1.0': b'10',
      }, impl.get_all(tmp) )
      
      bfile_metadata_factory_registry.clear_all()
      
  return _bfile_metadata_test_case

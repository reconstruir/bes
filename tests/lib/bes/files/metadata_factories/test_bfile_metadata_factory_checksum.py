#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
import os.path as path

from bes.files.bfile_checksum import bfile_checksum
from bes.files.bfile_date import bfile_date
from bes.files.metadata.bfile_metadata import bfile_metadata
from bes.files.metadata.bfile_metadata_error import bfile_metadata_error
from bes.files.metadata.bfile_metadata_factory_registry import bfile_metadata_factory_registry
from bes.files.metadata_factories.bfile_metadata_factory_checksum import bfile_metadata_factory_checksum
from bes.common.hash_util import hash_util
from bes.testing.unit_test import unit_test

class test_bfile_metadata_factory_checksum(unit_test):

  @classmethod
  def setUpClass(clazz):
    bfile_metadata_factory_registry.unregister_factory(bfile_metadata_factory_checksum)
    bfile_metadata_factory_registry.register_factory(bfile_metadata_factory_checksum)

  @classmethod
  def tearDownClass(clazz):
    bfile_metadata_factory_registry.unregister_factory(bfile_metadata_factory_checksum)
  
  def test_get_metadata(self):
    tmp = self.make_temp_file(dir = __file__, non_existent = True)
    #tmp_kiwi = self.make_temp_file(dir = __file__, content = 'this is kiwi')
    #tmp_lemon = self.make_temp_file(dir = __file__, content = 'this is lemon')

    with open(tmp, 'w') as fout:
      fout.write('kiwi')
      fout.flush()
      os.fsync(fout.fileno())

      self.assertEqual( hash_util.hash_string_md5('kiwi'),
                        bfile_metadata.get_metadata(tmp, 'bes/checksum/md5/0.0') )
      self.assertEqual( hash_util.hash_string_sha1('kiwi'),
                        bfile_metadata.get_metadata(tmp, 'bes/checksum/sha1/0.0') )
      self.assertEqual( hash_util.hash_string_sha256('kiwi'),
                        bfile_metadata.get_metadata(tmp, 'bes/checksum/sha256/0.0') )

      fout.seek(0)
      fout.truncate(0)
      fout.write('lemon')
      fout.flush()
      os.fsync(fout.fileno())

      self.assertEqual( hash_util.hash_string_md5('lemon'),
                        bfile_metadata.get_metadata(tmp, 'bes/checksum/md5/0.0') )
      self.assertEqual( hash_util.hash_string_sha1('lemon'),
                        bfile_metadata.get_metadata(tmp, 'bes/checksum/sha1/0.0') )
      self.assertEqual( hash_util.hash_string_sha256('lemon'),
                        bfile_metadata.get_metadata(tmp, 'bes/checksum/sha256/0.0') )
      
    return
#    hash_util.hash_string_md5()
      
    kiwi_checksums = {
      'md5': bfile_checksum.checksum(tmp_kiwi, 'md5'),
      'sha1': bfile_checksum.checksum(tmp_kiwi, 'sha1'),
      'sha256': bfile_checksum.checksum(tmp_kiwi, 'sha256'),
    }
    lemon_checksums = {
      'md5': bfile_checksum.checksum(tmp_lemon, 'md5'),
      'sha1': bfile_checksum.checksum(tmp_lemon, 'sha1'),
      'sha256': bfile_checksum.checksum(tmp_lemon, 'sha256'),
    }
    self.assertEqual( kiwi_checksums['md5'],
                      bfile_metadata.get_metadata(tmp_kiwi, 'bes/checksum/md5/0.0') )
    self.assertEqual( kiwi_checksums['sha1'],
                      bfile_metadata.get_metadata(tmp_kiwi, 'bes/checksum/sha1/0.0') )
    self.assertEqual( kiwi_checksums['sha256'],
                      bfile_metadata.get_metadata(tmp_kiwi, 'bes/checksum/sha256/0.0') )

    with open(tmp_kiwi, 'wb') as f:
      f.write(b'this is lemon')
      f.flush()
    bfile_date.touch(tmp_kiwi)
    
    self.assertEqual( lemon_checksums['md5'],
                      bfile_metadata.get_metadata(tmp_kiwi, 'bes/checksum/md5/0.0') )
    self.assertEqual( lemon_checksums['sha1'],
                      bfile_metadata.get_metadata(tmp_kiwi, 'bes/checksum/sha1/0.0') )
    self.assertEqual( lemon_checksums['sha256'],
                      bfile_metadata.get_metadata(tmp_kiwi, 'bes/checksum/sha256/0.0') )

    with open(tmp_lemon, 'wb') as f:
      f.write(b'this is kiwi')
      f.flush()
    bfile_date.touch(tmp_lemon)
    
    self.assertEqual( kiwi_checksums['md5'],
                      bfile_metadata.get_metadata(tmp_lemon, 'bes/checksum/md5/0.0') )
    self.assertEqual( kiwi_checksums['sha1'],
                      bfile_metadata.get_metadata(tmp_lemon, 'bes/checksum/sha1/0.0') )
    self.assertEqual( kiwi_checksums['sha256'],
                      bfile_metadata.get_metadata(tmp_lemon, 'bes/checksum/sha256/0.0') )

  def test_set_metadata_read_only(self):
    tmp = self.make_temp_file(dir = __file__, content = 'this is kiwi')
    self.assertEqual( bfile_checksum.checksum(tmp, 'sha256'), 
                      bfile_metadata.get_metadata(tmp, 'bes/checksum/sha256/0.0') )
    with self.assertRaises(bfile_metadata_error) as ex:
      bfile_metadata.set_metadata(tmp, 'bes/checksum/sha256/0.0', 'lime')

  def test_set_metadata(self):
    tmp = self.make_temp_file(dir = __file__, content = 'this is kiwi')
    self.assertEqual( bfile_checksum.checksum(tmp, 'sha256'), 
                      bfile_metadata.get_metadata(tmp, 'bes/checksum/sha256/0.0') )
    
if __name__ == '__main__':
  unit_test.main()

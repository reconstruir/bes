#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
import os.path as path

from bes.files.checksum.bf_checksum import bf_checksum
from bes.files.bf_date import bf_date
from bes.files.metadata.bf_metadata import bf_metadata
from bes.files.metadata.bf_metadata_error import bf_metadata_error
from bes.files.metadata.bf_metadata_factory_registry import bf_metadata_factory_registry
from bes.files.metadata_factories.bf_metadata_factory_checksum import bf_metadata_factory_checksum
from bes.common.hash_util import hash_util
from bes.testing.unit_test import unit_test

class test_bf_metadata_factory_checksum(unit_test):

  @classmethod
  def setUpClass(clazz):
    bf_metadata_factory_registry.register_factory(bf_metadata_factory_checksum)

  def test_get_metadata(self):
    tmp = self.make_temp_file(dir = __file__, non_existent = True)
    #tmp_kiwi = self.make_temp_file(dir = __file__, content = 'this is kiwi')
    #tmp_lemon = self.make_temp_file(dir = __file__, content = 'this is lemon')

    with open(tmp, 'w') as fout:
      fout.write('kiwi')
      fout.flush()
      os.fsync(fout.fileno())

      self.assertEqual( hash_util.hash_string_md5('kiwi'),
                        bf_metadata.get_metadata(tmp, 'bes__checksum__md5__0.0') )
      self.assertEqual( hash_util.hash_string_sha1('kiwi'),
                        bf_metadata.get_metadata(tmp, 'bes__checksum__sha1__0.0') )
      self.assertEqual( hash_util.hash_string_sha256('kiwi'),
                        bf_metadata.get_metadata(tmp, 'bes__checksum__sha256__0.0') )

      fout.seek(0)
      fout.truncate(0)
      fout.write('lemon')
      fout.flush()
      os.fsync(fout.fileno())

      self.assertEqual( hash_util.hash_string_md5('lemon'),
                        bf_metadata.get_metadata(tmp, 'bes__checksum__md5__0.0') )
      self.assertEqual( hash_util.hash_string_sha1('lemon'),
                        bf_metadata.get_metadata(tmp, 'bes__checksum__sha1__0.0') )
      self.assertEqual( hash_util.hash_string_sha256('lemon'),
                        bf_metadata.get_metadata(tmp, 'bes__checksum__sha256__0.0') )
      
    return
#    hash_util.hash_string_md5()
      
    kiwi_checksums = {
      'md5': bf_checksum.checksum(tmp_kiwi, 'md5'),
      'sha1': bf_checksum.checksum(tmp_kiwi, 'sha1'),
      'sha256': bf_checksum.checksum(tmp_kiwi, 'sha256'),
    }
    lemon_checksums = {
      'md5': bf_checksum.checksum(tmp_lemon, 'md5'),
      'sha1': bf_checksum.checksum(tmp_lemon, 'sha1'),
      'sha256': bf_checksum.checksum(tmp_lemon, 'sha256'),
    }
    self.assertEqual( kiwi_checksums['md5'],
                      bf_metadata.get_metadata(tmp_kiwi, 'bes__checksum__md5__0.0') )
    self.assertEqual( kiwi_checksums['sha1'],
                      bf_metadata.get_metadata(tmp_kiwi, 'bes__checksum__sha1__0.0') )
    self.assertEqual( kiwi_checksums['sha256'],
                      bf_metadata.get_metadata(tmp_kiwi, 'bes__checksum__sha256__0.0') )

    with open(tmp_kiwi, 'wb') as f:
      f.write(b'this is lemon')
      f.flush()
    bf_date.touch(tmp_kiwi)
    
    self.assertEqual( lemon_checksums['md5'],
                      bf_metadata.get_metadata(tmp_kiwi, 'bes__checksum__md5__0.0') )
    self.assertEqual( lemon_checksums['sha1'],
                      bf_metadata.get_metadata(tmp_kiwi, 'bes__checksum__sha1__0.0') )
    self.assertEqual( lemon_checksums['sha256'],
                      bf_metadata.get_metadata(tmp_kiwi, 'bes__checksum__sha256__0.0') )

    with open(tmp_lemon, 'wb') as f:
      f.write(b'this is kiwi')
      f.flush()
    bf_date.touch(tmp_lemon)
    
    self.assertEqual( kiwi_checksums['md5'],
                      bf_metadata.get_metadata(tmp_lemon, 'bes__checksum__md5__0.0') )
    self.assertEqual( kiwi_checksums['sha1'],
                      bf_metadata.get_metadata(tmp_lemon, 'bes__checksum__sha1__0.0') )
    self.assertEqual( kiwi_checksums['sha256'],
                      bf_metadata.get_metadata(tmp_lemon, 'bes__checksum__sha256__0.0') )
    
if __name__ == '__main__':
  unit_test.main()

#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.testing.unit_test import unit_test
from bes.files.metadata_factories.bfile_metadata_with_factories import bfile_metadata_with_factories
from bes.files.bfile_checksum import bfile_checksum

class test_bfile_metadata_with_factories(unit_test):

  # Use a temporary directory in the same filesystem as the code to avoid the
  # issue that on some platforms the tmp dir filesystem might have attributes disabled.
  _TMP_DIR = path.join(path.dirname(__file__), '.tmp')
  
  def test_factory_checksum(self):
    tmp_kiwi = self.make_temp_file(dir = self._TMP_DIR, content = 'this is kiwi')
    tmp_lemon = self.make_temp_file(dir = self._TMP_DIR, content = 'this is lemon')
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
                      bfile_metadata_with_factories.get_cached_metadata(tmp_kiwi, 'bes', 'checksum', 'md5', '0.0') )
    self.assertEqual( kiwi_checksums['sha1'],
                      bfile_metadata_with_factories.get_cached_metadata(tmp_kiwi, 'bes', 'checksum', 'sha1', '0.0') )
    self.assertEqual( kiwi_checksums['sha256'],
                      bfile_metadata_with_factories.get_cached_metadata(tmp_kiwi, 'bes', 'checksum', 'sha256', '0.0') )

    with open(tmp_kiwi, 'wb') as f:
      f.write(b'this is lemon')
      f.flush()

    self.assertEqual( lemon_checksums['md5'],
                      bfile_metadata_with_factories.get_cached_metadata(tmp_kiwi, 'bes', 'checksum', 'md5', '0.0') )
    self.assertEqual( lemon_checksums['sha1'],
                      bfile_metadata_with_factories.get_cached_metadata(tmp_kiwi, 'bes', 'checksum', 'sha1', '0.0') )
    self.assertEqual( lemon_checksums['sha256'],
                      bfile_metadata_with_factories.get_cached_metadata(tmp_kiwi, 'bes', 'checksum', 'sha256', '0.0') )

    with open(tmp_lemon, 'wb') as f:
      f.write(b'this is kiwi')
      f.flush()

    self.assertEqual( kiwi_checksums['md5'],
                      bfile_metadata_with_factories.get_cached_metadata(tmp_lemon, 'bes', 'checksum', 'md5', '0.0') )
    self.assertEqual( kiwi_checksums['sha1'],
                      bfile_metadata_with_factories.get_cached_metadata(tmp_lemon, 'bes', 'checksum', 'sha1', '0.0') )
    self.assertEqual( kiwi_checksums['sha256'],
                      bfile_metadata_with_factories.get_cached_metadata(tmp_lemon, 'bes', 'checksum', 'sha256', '0.0') )
      
    bfile_metadata_with_factories.clear_all_factories()

if __name__ == '__main__':
  unit_test.main()

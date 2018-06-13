#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import unittest
from bes.fs import temp_file
from bes.caca_archive.caca_archive_extension import caca_archive_extension
from bes.caca_archive.temp_caca_archive import temp_caca_archive
from bes.caca_archive.caca_archive_xz import caca_archive_xz
from caca_caca_archive_base_common import caca_caca_archive_base_common

class test_caca_archive_xz(unittest.TestCase, caca_caca_archive_base_common):

  def __init__(self, methodName = 'runTest'):
    super(test_caca_archive_xz, self).__init__(methodName)
    self.default_caca_archive_type = caca_archive_extension.XZ

  def make_caca_archive(self, filename):
    return caca_archive_xz(filename)

  def test_init(self):
    self.assertEqual( 'foo.xz', caca_archive_xz('foo.xz').filename )

  def test_file_is_valid(self):
    tmp_zip = temp_caca_archive.make_temp_caca_archive([ temp_caca_archive.Item('foo.txt', content = 'foo.txt\n') ], caca_archive_extension.ZIP)
    self.assertFalse( caca_archive_xz.file_is_valid(tmp_zip.filename) )

    tmp_tar = temp_caca_archive.make_temp_caca_archive([ temp_caca_archive.Item('foo.txt', content = 'foo.txt\n') ], caca_archive_extension.TAR)
    self.assertFalse( caca_archive_xz.file_is_valid(tmp_tar.filename) )

    tmp_tgz = temp_caca_archive.make_temp_caca_archive([ temp_caca_archive.Item('foo.txt', content = 'foo.txt\n') ], caca_archive_extension.TGZ)
    self.assertFalse( caca_archive_xz.file_is_valid(tmp_tgz.filename) )

    tmp_tar_gz = temp_caca_archive.make_temp_caca_archive([ temp_caca_archive.Item('foo.txt', content = 'foo.txt\n') ], caca_archive_extension.TAR_GZ)
    self.assertFalse( caca_archive_xz(tmp_).file_is_valid(tar_gz.filename) )

    tmp_xz = temp_caca_archive.make_temp_caca_archive([ temp_caca_archive.Item('foo.txt', content = 'foo.txt\n') ], caca_archive_extension.XZ)
    self.assertTrue( caca_archive_xz.file_is_valid(tmp_xz.filename) )

    self.assertFalse( caca_archive_xz.file_is_valid(temp_file.make_temp_file(content = 'junk\n')) )
    
if __name__ == "__main__":
  unittest.main()

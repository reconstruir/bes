#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import unittest
from bes.fs import temp_file
from bes.caca_archive.caca_archive_extension import caca_archive_extension
from bes.caca_archive.temp_caca_archive import temp_caca_archive
from bes.caca_archive.caca_archive_zip import caca_archive_zip
from caca_caca_common_archive_tests import caca_caca_common_archive_tests

class test_caca_archive_zip(unittest.TestCase, caca_caca_common_archive_tests):

  def __init__(self, methodName = 'runTest'):
    super(test_caca_archive_zip, self).__init__(methodName)
    self.default_caca_archive_type = caca_archive_extension.ZIP

  def make_caca_archive(self, filename):
    return caca_archive_zip(filename)

  def test_init(self):
    self.assertEqual( 'foo.zip', caca_archive_zip('foo.zip').filename )

  def test_file_is_valid(self):
    tmp_zip = temp_caca_archive.make_temp_caca_archive([ temp_caca_archive.Item('foo.txt', content = 'foo.txt\n') ], caca_archive_extension.ZIP)
    self.assertTrue( caca_archive_zip.file_is_valid(tmp_zip.filename) )

    tmp_tar = temp_caca_archive.make_temp_caca_archive([ temp_caca_archive.Item('foo.txt', content = 'foo.txt\n') ], caca_archive_extension.TAR)
    self.assertFalse( caca_archive_zip.file_is_valid(tmp_tar.filename) )

    tmp_tgz = temp_caca_archive.make_temp_caca_archive([ temp_caca_archive.Item('foo.txt', content = 'foo.txt\n') ], caca_archive_extension.TGZ)
    self.assertFalse( caca_archive_zip.file_is_valid(tmp_tgz.filename) )

    tmp_tar_gz = temp_caca_archive.make_temp_caca_archive([ temp_caca_archive.Item('foo.txt', content = 'foo.txt\n') ], caca_archive_extension.TAR_GZ)
    self.assertFalse( caca_archive_zip.file_is_valid(tmp_tar_gz.filename) )

    self.assertFalse( caca_archive_zip.file_is_valid(temp_file.make_temp_file(content = 'junk\n')) )

if __name__ == "__main__":
  unittest.main()

#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import unittest
from bes.fs import temp_file
from bes.archive.archive_extension import archive_extension
from bes.archive.temp_archive import temp_archive
from bes.archive.archive_tar import archive_tar
from common_archive_tests import common_archive_tests

class test_archive_tar(unittest.TestCase, common_archive_tests):

  def __init__(self, methodName = 'runTest'):
    super(test_archive_tar, self).__init__(methodName)
    self.default_archive_type = archive_extension.TAR

  def _make_archive(self, filename):
    return archive_tar(filename)

  def test_init(self):
    self.assertEqual( 'foo.tar', archive_tar('foo.tar').filename )

  def test_file_is_valid(self):
    tmp_tar = temp_archive.make_temp_archive([ temp_archive.Item('foo.txt', content = 'foo.txt\n') ], archive_extension.TAR)
    self.assertTrue( archive_tar.file_is_valid(tmp_tar.filename) )

    tmp_tgz = temp_archive.make_temp_archive([ temp_archive.Item('foo.txt', content = 'foo.txt\n') ], archive_extension.TGZ)
    self.assertTrue( archive_tar.file_is_valid(tmp_tgz.filename) )

    tmp_tar_gz = temp_archive.make_temp_archive([ temp_archive.Item('foo.txt', content = 'foo.txt\n') ], archive_extension.TAR_GZ)
    self.assertTrue( archive_tar.file_is_valid(tmp_tar_gz.filename) )

    tmp_zip = temp_archive.make_temp_archive([ temp_archive.Item('foo.txt', content = 'foo.txt\n') ], archive_extension.ZIP)
    self.assertFalse( archive_tar.file_is_valid(tmp_zip.filename) )

    self.assertFalse( archive_tar.file_is_valid(temp_file.make_temp_file(content = 'junk\n')) )
    
if __name__ == "__main__":
  unittest.main()

#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.fs import temp_file
from bes.archive.archive_extension import archive_extension
from bes.archive.temp_archive import temp_archive
from bes.archive.archive_zip import archive_zip
from common_archive_tests import common_archive_tests

class test_archive_zip(unit_test, common_archive_tests):

  def __init__(self, methodName = 'runTest'):
    super(test_archive_zip, self).__init__(methodName)
    self.default_archive_type = archive_extension.ZIP

  def _make_archive(self, filename):
    return archive_zip(filename)

  def test_init(self):
    self.assertEqual( 'foo.zip', archive_zip('foo.zip').filename )

  def test_file_is_valid(self):
    tmp_zip = temp_archive.make_temp_archive([ temp_archive.item('foo.txt', content = 'foo.txt\n') ], archive_extension.ZIP)
    self.assertTrue( archive_zip.file_is_valid(tmp_zip.filename) )

    tmp_tar = temp_archive.make_temp_archive([ temp_archive.item('foo.txt', content = 'foo.txt\n') ], archive_extension.TAR)
    self.assertFalse( archive_zip.file_is_valid(tmp_tar.filename) )

    tmp_tgz = temp_archive.make_temp_archive([ temp_archive.item('foo.txt', content = 'foo.txt\n') ], archive_extension.TGZ)
    self.assertFalse( archive_zip.file_is_valid(tmp_tgz.filename) )

    tmp_tar_gz = temp_archive.make_temp_archive([ temp_archive.item('foo.txt', content = 'foo.txt\n') ], archive_extension.TAR_GZ)
    self.assertFalse( archive_zip.file_is_valid(tmp_tar_gz.filename) )

    self.assertFalse( archive_zip.file_is_valid(temp_file.make_temp_file(content = 'junk\n')) )

if __name__ == '__main__':
  unit_test.main()

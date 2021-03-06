#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.fs import temp_file
from bes.archive.archive_extension import archive_extension
from bes.archive.temp_archive import temp_archive
from bes.archive.archive_xz import archive_xz
from common_archive_tests import common_archive_tests
from bes.testing.unit_test.unit_test_skip import raise_skip

class test_archive_xz(unit_test, common_archive_tests):

  @classmethod
  def setUpClass(clazz):
    pass
    #raise_skip('broken')
  
  def __init__(self, methodName = 'runTest'):
    super(test_archive_xz, self).__init__(methodName)
    self.default_archive_type = archive_extension.XZ

  def _make_archive(self, filename):
    return archive_xz(filename)

  def test_init(self):
    self.assertEqual( 'foo.xz', archive_xz('foo.xz').filename )

  def test_file_is_valid(self):
    tmp_zip = temp_archive.make_temp_archive([ temp_archive.item('foo.txt', content = 'foo.txt\n') ], archive_extension.ZIP)
    self.assertFalse( archive_xz.file_is_valid(tmp_zip.filename) )

    tmp_tar = temp_archive.make_temp_archive([ temp_archive.item('foo.txt', content = 'foo.txt\n') ], archive_extension.TAR)
    self.assertFalse( archive_xz.file_is_valid(tmp_tar.filename) )

    tmp_tgz = temp_archive.make_temp_archive([ temp_archive.item('foo.txt', content = 'foo.txt\n') ], archive_extension.TGZ)
    self.assertFalse( archive_xz.file_is_valid(tmp_tgz.filename) )

    tmp_tar_gz = temp_archive.make_temp_archive([ temp_archive.item('foo.txt', content = 'foo.txt\n') ], archive_extension.TAR_GZ)
    self.assertFalse( archive_xz.file_is_valid(tmp_tar_gz.filename) )

    tmp_xz = temp_archive.make_temp_archive([ temp_archive.item('foo.txt', content = 'foo.txt\n') ], archive_extension.XZ)
    self.assertTrue( archive_xz.file_is_valid(tmp_xz.filename) )

    self.assertFalse( archive_xz.file_is_valid(temp_file.make_temp_file(content = 'junk\n')) )
    
if __name__ == '__main__':
  unit_test.main()

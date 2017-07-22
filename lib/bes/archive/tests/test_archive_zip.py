#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

import unittest
from bes.archive.archive_extension import archive_extension
from bes.archive.temp_archive import temp_archive
from bes.archive.archive_zip import archive_zip
from archive_base_common import archive_base_common

class test_archive_zip(unittest.TestCase, archive_base_common):

  def __init__(self, methodName = 'runTest'):
    super(test_archive_zip, self).__init__(methodName)
    self.default_archive_type = archive_extension.ZIP

  def make_archive(self, filename):
    return archive_zip(filename)

  def test_init(self):
    self.assertEqual( 'foo.zip', archive_zip('foo.zip').filename )

  def test_is_valid(self):
    tmp_zip = temp_archive.make_temp_archive([ temp_archive.Item('foo.txt', content = 'foo.txt\n') ], archive_extension.ZIP)
    self.assertTrue( archive_zip(tmp_zip.filename).is_valid() )

    tmp_tar = temp_archive.make_temp_archive([ temp_archive.Item('foo.txt', content = 'foo.txt\n') ], archive_extension.TAR)
    self.assertFalse( archive_zip(tmp_tar.filename).is_valid() )

    tmp_tgz = temp_archive.make_temp_archive([ temp_archive.Item('foo.txt', content = 'foo.txt\n') ], archive_extension.TGZ)
    self.assertFalse( archive_zip(tmp_tgz.filename).is_valid() )

    tmp_tar_gz = temp_archive.make_temp_archive([ temp_archive.Item('foo.txt', content = 'foo.txt\n') ], archive_extension.TAR_GZ)
    self.assertFalse( archive_zip(tmp_tar_gz.filename).is_valid() )

if __name__ == "__main__":
  unittest.main()

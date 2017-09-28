#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

import os.path as path, tarfile, unittest, zipfile
from bes.fs import file_util, temp_file
from bes.archive.temp_archive import temp_archive

class Testtemp_archive(unittest.TestCase):

  def test_make_temp_archive_tgz(self):
    a = temp_archive.make_temp_archive([ temp_archive.Item('foo.txt', content = 'foo.txt\n') ], 'tgz')
    self.assertTrue( path.isfile(a.filename) )
    self.assertTrue( tarfile.is_tarfile(a.filename) )
    self.assertFalse( zipfile.is_zipfile(a.filename) )

  def test_make_temp_archive_bz2(self):
    a = temp_archive.make_temp_archive([ temp_archive.Item('foo.txt', content = 'foo.txt\n') ], 'tar.bz2')
    self.assertTrue( path.isfile(a.filename) )
    self.assertTrue( tarfile.is_tarfile(a.filename) )
    self.assertFalse( zipfile.is_zipfile(a.filename) )

  def test_make_temp_archive_tar(self):
    a = temp_archive.make_temp_archive([ temp_archive.Item('foo.txt', content = 'foo.txt\n') ], 'tar')
    self.assertTrue( path.isfile(a.filename) )
    self.assertTrue( tarfile.is_tarfile(a.filename) )
    self.assertFalse( zipfile.is_zipfile(a.filename) )

  def test_make_temp_archive_zip(self):
    a = temp_archive.make_temp_archive([ temp_archive.Item('foo.txt', content = 'foo.txt\n') ], 'zip')
    self.assertTrue( path.isfile(a.filename) )
    self.assertTrue( zipfile.is_zipfile(a.filename) )
    self.assertFalse( tarfile.is_tarfile(a.filename) )

  def test_make_temp_archive_from_file(self):
    tmp_file = temp_file.make_temp_file(content = 'foo.txt\n', suffix = '.foo.txt')
    tmp_archive = temp_archive.make_temp_archive([ temp_archive.Item('foo.txt', filename = tmp_file) ], 'tgz')
    self.assertTrue( path.isfile(tmp_archive.filename) )
    self.assertTrue( tarfile.is_tarfile(tmp_archive.filename) )
    self.assertFalse( zipfile.is_zipfile(tmp_archive.filename) )
    tmp_dir = temp_file.make_temp_dir()

    with tarfile.open(tmp_archive.filename, mode = 'r') as archive:
      archive.extractall(path = tmp_dir)
      tmp_member_path = path.join(tmp_dir, 'foo.txt')
      self.assertTrue( path.isfile(tmp_member_path) )
      self.assertEqual( b'foo.txt\n', file_util.read(tmp_member_path) )
    
if __name__ == "__main__":
  unittest.main()

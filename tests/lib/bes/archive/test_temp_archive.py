#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

import os.path as path, tarfile, zipfile
from bes.testing.unit_test import unit_test
from bes.fs import file_util, temp_file
from bes.archive.temp_archive import temp_archive
from bes.archive.macos import dmg

class test_temp_archive(unit_test):

  DEBUG = unit_test.DEBUG
  #DEBUG = True
  
  def test_make_temp_archive_tgz(self):
    a = self._make_temp_archive('tgz')
    self.assertTrue( path.isfile(a.filename) )
    self.assertTrue( tarfile.is_tarfile(a.filename) )
    self.assertFalse( zipfile.is_zipfile(a.filename) )

  def test_make_temp_archive_bz2(self):
    a = self._make_temp_archive('tar.bz2')
    self.assertTrue( path.isfile(a.filename) )
    self.assertTrue( tarfile.is_tarfile(a.filename) )
    self.assertFalse( zipfile.is_zipfile(a.filename) )

  def test_make_temp_archive_tar(self):
    a = self._make_temp_archive('tar')
    self.assertTrue( path.isfile(a.filename) )
    self.assertTrue( tarfile.is_tarfile(a.filename) )
    self.assertFalse( zipfile.is_zipfile(a.filename) )

  def test_make_temp_archive_dmg(self):
    a = self._make_temp_archive('dmg')
    self.assertTrue( path.isfile(a.filename) )
    self.assertFalse( tarfile.is_tarfile(a.filename) )
    self.assertFalse( zipfile.is_zipfile(a.filename) )
    self.spew('checking: %s' % (a.filename))
    self.assertTrue( dmg.is_dmg_file(a.filename) )

  def test_make_temp_archive_zip(self):
    a = self._make_temp_archive('zip')
    self.assertTrue( path.isfile(a.filename) )
    self.assertTrue( zipfile.is_zipfile(a.filename) )
    self.assertFalse( tarfile.is_tarfile(a.filename) )

  def test_make_temp_archive_from_file(self):
    tmp_file = temp_file.make_temp_file(content = 'foo.txt\n', suffix = '.foo.txt')
    tmp_archive = self._make_temp_archive('tgz', items = [ temp_archive.Item('foo.txt', filename = tmp_file) ])
    self.assertTrue( path.isfile(tmp_archive.filename) )
    self.assertTrue( tarfile.is_tarfile(tmp_archive.filename) )
    self.assertFalse( zipfile.is_zipfile(tmp_archive.filename) )
    tmp_dir = temp_file.make_temp_dir()

    with tarfile.open(tmp_archive.filename, mode = 'r') as archive:
      archive.extractall(path = tmp_dir)
      tmp_member_path = path.join(tmp_dir, 'foo.txt')
      self.assertTrue( path.isfile(tmp_member_path) )
      self.assertEqual( b'foo.txt\n', file_util.read(tmp_member_path) )

  def _make_temp_archive(self, extension, items = None):
    items = items or [ temp_archive.Item('foo.txt', content = 'foo.txt\n') ]
    ta = temp_archive.make_temp_archive(items, extension, delete = not self.DEBUG)
    if self.DEBUG:
      self.spew('temp_archive(%s): %s' % (extension, ta))
    return ta
      
if __name__ == "__main__":
  unit_test.main()

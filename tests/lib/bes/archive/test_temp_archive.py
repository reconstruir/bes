#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path, tarfile, zipfile
from bes.testing.unit_test import unit_test
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file
from bes.system.host import host
from bes.archive.temp_archive import temp_archive
from bes.archive.macos.dmg import dmg
from bes.testing.unit_test_function_skip import unit_test_function_skip

class test_temp_archive(unit_test):

  DEBUG = unit_test.DEBUG
  #DEBUG = True
  
  def test_make_temp_archive_tgz(self):
    a = self._make_temp_archive('tgz')
    self.assertTrue( path.isfile(a) )
    self.assertTrue( tarfile.is_tarfile(a) )
    self.assertFalse( zipfile.is_zipfile(a) )

  def test_make_temp_archive_bz2(self):
    a = self._make_temp_archive('tar.bz2')
    self.assertTrue( path.isfile(a) )
    self.assertTrue( tarfile.is_tarfile(a) )
    self.assertFalse( zipfile.is_zipfile(a) )

  def test_make_temp_archive_tar(self):
    a = self._make_temp_archive('tar')
    self.assertTrue( path.isfile(a) )
    self.assertTrue( tarfile.is_tarfile(a) )
    self.assertFalse( zipfile.is_zipfile(a) )

  @unit_test_function_skip.skip_if(not host.is_macos(), 'dmg is only supported on macos')
  def test_make_temp_archive_dmg(self):
    a = self._make_temp_archive('dmg')
    self.assertTrue( path.isfile(a) )
    self.assertFalse( tarfile.is_tarfile(a) )
    self.assertFalse( zipfile.is_zipfile(a) )
    self.spew('checking: %s' % (a))
    self.assertTrue( dmg.is_dmg_file(a) )

  def test_make_temp_archive_zip(self):
    a = self._make_temp_archive('zip')
    self.assertTrue( path.isfile(a) )
    self.assertTrue( zipfile.is_zipfile(a) )
    self.assertFalse( tarfile.is_tarfile(a) )

  def test_make_temp_archive_from_file(self):
    tmp_file = temp_file.make_temp_file(content = 'foo.txt\n', suffix = '.foo.txt')
    tmp_archive = self._make_temp_archive('tgz', items = [ temp_archive.item('foo.txt', filename = tmp_file) ])
    self.assertTrue( path.isfile(tmp_archive) )
    self.assertTrue( tarfile.is_tarfile(tmp_archive) )
    self.assertFalse( zipfile.is_zipfile(tmp_archive) )
    tmp_dir = temp_file.make_temp_dir()

    with tarfile.open(tmp_archive, mode = 'r') as archive:
      archive.extractall(path = tmp_dir, filter = lambda info, _: info)
      tmp_member_path = path.join(tmp_dir, 'foo.txt')
      self.assertTrue( path.isfile(tmp_member_path) )
      self.assertEqual( b'foo.txt\n', file_util.read(tmp_member_path) )

  def _make_temp_archive(self, extension, items = None):
    items = items or [ temp_archive.item('foo.txt', content = 'foo.txt\n') ]
    ta = temp_archive.make_temp_archive(items, extension, delete = not self.DEBUG)
    if self.DEBUG:
      self.spew('temp_archive(%s): %s' % (extension, ta))
    return ta
      
if __name__ == "__main__":
  unit_test.main()

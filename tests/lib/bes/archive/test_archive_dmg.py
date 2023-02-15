#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from bes.fs.temp_file import temp_file
from bes.system.host import host
from bes.archive.archive_extension import archive_extension
from bes.archive.temp_archive import temp_archive
from bes.archive.archive_dmg import archive_dmg
from bes.testing.unit_test_class_skip import unit_test_class_skip
from bes.fs.testing.temp_content import temp_content
from bes.system.execute import execute

class test_archive_dmg(unit_test):

  __unit_test_data_dir__ = '${BES_TEST_DATA_DIR}/lib/bes/archive/dmg'

  @classmethod
  def setUpClass(clazz):
    unit_test_class_skip.raise_skip_if_not_platform(host.MACOS)
  
  def __init__(self, methodName = 'runTest'):
    super(test_archive_dmg, self).__init__(methodName)
    self.default_archive_type = archive_extension.DMG

  def _make_archive(self, filename):
    return archive_dmg(filename)

  def test_init(self):
    self.assertEqual( 'foo.dmg', archive_dmg('foo.dmg').filename )

  def test_file_is_valid(self):
    tmp_dmg = self._make_test_dmg()
    self.assertTrue( archive_dmg.file_is_valid(tmp_dmg) )

    tmp_zip = temp_archive.make_temp_archive([ temp_archive.item('foo.txt', content = 'foo.txt\n') ], archive_extension.ZIP)
    self.assertFalse( archive_dmg.file_is_valid(tmp_zip) )

    tmp_tar = temp_archive.make_temp_archive([ temp_archive.item('foo.txt', content = 'foo.txt\n') ], archive_extension.TAR)
    self.assertFalse( archive_dmg.file_is_valid(tmp_tar) )

    tmp_tgz = temp_archive.make_temp_archive([ temp_archive.item('foo.txt', content = 'foo.txt\n') ], archive_extension.TGZ)
    self.assertFalse( archive_dmg.file_is_valid(tmp_tgz) )

    tmp_tar_gz = temp_archive.make_temp_archive([ temp_archive.item('foo.txt', content = 'foo.txt\n') ], archive_extension.TAR_GZ)
    self.assertFalse( archive_dmg.file_is_valid(tmp_tar_gz) )

    self.assertFalse( archive_dmg.file_is_valid(temp_file.make_temp_file(content = 'junk\n')) )
    
  def test_members(self):
    tmp_dmg = self._make_test_dmg()
    self.assertEqual( [ 'foo.txt', 'link_to_foo.txt', 'subdir/bar.txt' ], archive_dmg(tmp_dmg).members )
    
  def test_extract_all(self):
    tmp_dir = temp_file.make_temp_dir(delete = not self.DEBUG)
    tmp_dmg = self._make_test_dmg()
    archive_dmg(tmp_dmg).extract_all(tmp_dir)
    self.assertTrue( path.isfile(path.join(tmp_dir, 'foo.txt')) )
#    self.assertTrue( path.islink(path.join(tmp_dir, 'link_to_foo.txt')) )
    self.assertTrue( path.isfile(path.join(tmp_dir, 'subdir/bar.txt')) )

  def _make_test_dmg(self):
    tmp_dir = self.make_temp_dir()
    temp_content.write_items([
      'file subdir/bar.txt "bar.txt\n" 644',
      'file foo.txt "foo.txt\n" 644',
      'file link_to_foo.txt "foo.txt\n" 644',
    ], path.join(tmp_dir, 'exampledir'))
    tmp_dmg = self.make_temp_file(suffix = '.dmg')
    cmd = [
      'hdiutil',
      'create',
      '-volname', 'examplevol',
      '-srcfolder', 'exampledir',
      '-ov',
      '-format', 'UDZO',
      tmp_dmg,
    ]
    execute.execute(cmd, cwd = tmp_dir)
    if self.DEBUG:
      print(f'tmp_dmg={tmp_dmg}')
    return tmp_dmg
    
if __name__ == '__main__':
  unit_test.main()

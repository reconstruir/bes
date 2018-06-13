#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from bes.fs import temp_file
from bes.system import host
from bes.caca_archive.caca_archive_extension import caca_archive_extension
from bes.caca_archive.temp_caca_archive import temp_caca_archive
from bes.caca_archive.caca_archive_dmg import caca_archive_dmg
from bes.caca_archive.temp_caca_archive import temp_caca_archive
from bes.testing.unit_test.unit_test_skip import raise_skip_if_not_platform

#class test_caca_archive_dmg(unit_test, caca_caca_archive_base_common): # too slow
class test_caca_archive_dmg(unit_test):

  __unit_test_data_dir__ = '${BES_TEST_DATA_DIR}/lib/bes/caca_archive/dmg'

  @classmethod
  def setUpClass(clazz):
    raise_skip_if_not_platform(host.MACOS)
  
  def __init__(self, methodName = 'runTest'):
    super(test_caca_archive_dmg, self).__init__(methodName)
    self.default_caca_archive_type = caca_archive_extension.DMG

  def make_caca_archive(self, filename):
    return caca_archive_dmg(filename)

  def test_init(self):
    self.assertEqual( 'foo.dmg', caca_archive_dmg('foo.dmg').filename )

  def test_file_is_valid(self):
    self.assertTrue( caca_archive_dmg.file_is_valid(self.data_path('example.dmg')) )

    tmp_zip = temp_caca_archive.make_temp_caca_archive([ temp_caca_archive.Item('foo.txt', content = 'foo.txt\n') ], caca_archive_extension.ZIP)
    self.assertFalse( caca_archive_dmg.file_is_valid(tmp_zip.filename) )

    tmp_tar = temp_caca_archive.make_temp_caca_archive([ temp_caca_archive.Item('foo.txt', content = 'foo.txt\n') ], caca_archive_extension.TAR)
    self.assertFalse( caca_archive_dmg.file_is_valid(tmp_tar.filename) )

    tmp_tgz = temp_caca_archive.make_temp_caca_archive([ temp_caca_archive.Item('foo.txt', content = 'foo.txt\n') ], caca_archive_extension.TGZ)
    self.assertFalse( caca_archive_dmg.file_is_valid(tmp_tgz.filename) )

    tmp_tar_gz = temp_caca_archive.make_temp_caca_archive([ temp_caca_archive.Item('foo.txt', content = 'foo.txt\n') ], caca_archive_extension.TAR_GZ)
    self.assertFalse( caca_archive_dmg(tmp_).file_is_valid(tar_gz.filename) )

    self.assertFalse( caca_archive_dmg.file_is_valid(temp_file.make_temp_file(content = 'junk\n')) )
    
  def test_members(self):
    self.assertEqual( [ 'foo.txt', 'link_to_foo.sh', 'subdir/bar.txt' ], caca_archive_dmg(self.data_path('example.dmg')).members() )
    
  def test_extract(self):
    tmp_dir = temp_file.make_temp_dir(delete = False)
    caca_archive_dmg(self.data_path('example.dmg')).extract(tmp_dir)
    self.assertTrue( path.isfile(path.join(tmp_dir, 'foo.txt')) )
#    self.assertTrue( path.islink(path.join(tmp_dir, 'link_to_foo.sh')) )
    self.assertTrue( path.isfile(path.join(tmp_dir, 'subdir/bar.txt')) )
    
if __name__ == '__main__':
  unit_test.main()

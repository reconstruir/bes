#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from bes.fs import temp_file
from bes.system import host
from bes.archive.archive_extension import archive_extension
from bes.archive.temp_archive import temp_archive
from bes.archive.archive_dmg import archive_dmg
from bes.archive.temp_archive import temp_archive
from bes.testing.unit_test.unit_test_skip import raise_skip_if_not_platform

#class test_archive_dmg(unit_test, archive_base_common): # too slow
class test_archive_dmg(unit_test):

  __unit_test_data_dir__ = '${BES_TEST_DATA_DIR}/lib/bes/archive/dmg'

  @classmethod
  def setUpClass(clazz):
    raise_skip_if_not_platform(host.MACOS)
  
  def __init__(self, methodName = 'runTest'):
    super(test_archive_dmg, self).__init__(methodName)
    self.default_archive_type = archive_extension.DMG

  def make_archive(self, filename):
    return archive_dmg(filename)

  def test_init(self):
    self.assertEqual( 'foo.dmg', archive_dmg('foo.dmg').filename )

  def test_is_valid(self):
    self.assertTrue( archive_dmg(self.data_path('example.dmg')).is_valid() )

    tmp_zip = temp_archive.make_temp_archive([ temp_archive.Item('foo.txt', content = 'foo.txt\n') ], archive_extension.ZIP)
    self.assertFalse( archive_dmg(tmp_zip.filename).is_valid() )

    tmp_tar = temp_archive.make_temp_archive([ temp_archive.Item('foo.txt', content = 'foo.txt\n') ], archive_extension.TAR)
    self.assertFalse( archive_dmg(tmp_tar.filename).is_valid() )

    tmp_tgz = temp_archive.make_temp_archive([ temp_archive.Item('foo.txt', content = 'foo.txt\n') ], archive_extension.TGZ)
    self.assertFalse( archive_dmg(tmp_tgz.filename).is_valid() )

    tmp_tar_gz = temp_archive.make_temp_archive([ temp_archive.Item('foo.txt', content = 'foo.txt\n') ], archive_extension.TAR_GZ)
    self.assertFalse( archive_dmg(tmp_tar_gz.filename).is_valid() )

    self.assertFalse( archive_dmg(temp_file.make_temp_file(content = 'junk\n')).is_valid() )
    
  def test_members(self):
    self.assertEqual( [ 'foo.txt', 'link_to_foo.sh', 'subdir/bar.txt' ], archive_dmg(self.data_path('example.dmg')).members() )
    
  def test_extract(self):
    tmp_dir = temp_file.make_temp_dir(delete = False)
    archive_dmg(self.data_path('example.dmg')).extract(tmp_dir)
    self.assertTrue( path.isfile(path.join(tmp_dir, 'foo.txt')) )
#    self.assertTrue( path.islink(path.join(tmp_dir, 'link_to_foo.sh')) )
    self.assertTrue( path.isfile(path.join(tmp_dir, 'subdir/bar.txt')) )
    
if __name__ == '__main__':
  unit_test.main()

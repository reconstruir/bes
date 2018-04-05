#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test

from bes.archive.archive_extension import archive_extension
from bes.archive.temp_archive import temp_archive
from bes.archive.archive_dmg import archive_dmg
from archive_base_common import archive_base_common
from bes.archive.temp_archive import temp_archive

#class test_archive_dmg(unit_test, archive_base_common):
class test_archive_dmg(unit_test):

  __unit_test_data_dir__ = '${BES_TEST_DATA_DIR}/lib/bes/archive/dmg'
  
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

  def test_members(self):
    assert self.default_archive_type
    tmp_tar = temp_archive.make_temp_archive([ temp_archive.Item('foo.txt', content = 'foo.txt\n') ], self.default_archive_type)
    self.assertEqual( [ 'foo.txt' ], self.make_archive(tmp_tar.filename).members() )
    
  def test_extract(self):
    assert self.default_archive_type
    items = temp_archive.make_temp_item_list([
      ( 'foo.txt', 'foo.txt\n' ),
    ])
    tmp_archive = self.make_temp_archive_for_reading(items)
    tmp_dir = temp_file.make_temp_dir()
    tmp_archive.extract(tmp_dir)
    self.assertTrue( path.isfile(path.join(tmp_dir, 'foo.txt')) )
    
if __name__ == '__main__':
  unit_test.main()

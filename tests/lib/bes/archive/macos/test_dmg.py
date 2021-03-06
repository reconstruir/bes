#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test

import os.path as path, pprint
from bes.fs import file_find, file_util, temp_file
from bes.system import host
from bes.archive.macos import dmg
from bes.testing.unit_test.unit_test_skip import raise_skip_if_not_platform

class test_dmg(unit_test):

  __unit_test_data_dir__ = '${BES_TEST_DATA_DIR}/lib/bes/archive/dmg'

  @classmethod
  def setUpClass(clazz):
    raise_skip_if_not_platform(host.MACOS)

  def test_info(self):
    info = dmg.info()
    #self.spew(pprint.pformat(info))

  def test_contents(self):
    expected = [ 'foo.txt', 'link_to_foo.sh', 'subdir/bar.txt' ]
    info1 = dmg.info()
    actual = dmg.contents(self.data_path('example.dmg'))
    info2 = dmg.info()
    self.assertEqual( expected, actual )
    #self.assertEqual( info1, info2 )

  def test_is_dmg_file(self):
    self.assertTrue( dmg.is_dmg_file(self.data_path('example.dmg')) )

  def test_extract_all(self):
    tmp_dir = temp_file.make_temp_dir()
    info1 = dmg.info()
    dmg.extract(self.data_path('example.dmg'), tmp_dir)
    info2 = dmg.info()
    files = file_find.find(tmp_dir, relative = True, file_type = file_find.FILE_OR_LINK)
    self.assertEqual( [ 'foo.txt', 'link_to_foo.sh', 'subdir/bar.txt' ], files )
    #self.assertEqual( info1, info2 )
    
if __name__ == '__main__':
  unit_test.main()

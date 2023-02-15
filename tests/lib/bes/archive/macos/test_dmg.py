#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test

import os.path as path, pprint
from bes.fs.file_find import file_find
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file
from bes.system.host import host
from bes.system.execute import execute
from bes.archive.macos.dmg import dmg
from bes.testing.unit_test_class_skip import unit_test_class_skip
from bes.fs.testing.temp_content import temp_content

class test_dmg(unit_test):

  def __init__(self, *args, **kargs):
    super(test_dmg, self).__init__(*args, **kargs)
    dmg.set_debug(self.DEBUG)
  
  @classmethod
  def setUpClass(clazz):
    unit_test_class_skip.raise_skip_if_not_platform(host.MACOS)

  def test_info(self):
    info = dmg.info()
    self.spew(pprint.pformat(info))

  def test_contents(self):
    expected = [ 'foo.txt', 'link_to_foo.txt', 'subdir/bar.txt' ]
    info1 = dmg.info()
    tmp_dmg = self._tmp_example_dmg('example.dmg')
    actual = dmg.contents(tmp_dmg)
    info2 = dmg.info()
    self.assertEqual( expected, actual )
    #self.assertEqual( info1, info2 )

  def test_is_dmg_file(self):
    self.assertTrue( dmg.is_dmg_file(self._tmp_example_dmg('example.dmg')) )

  def test_extract_all(self):
    tmp_dir = temp_file.make_temp_dir()
    info1 = dmg.info()
    dmg.extract(self._tmp_example_dmg('example.dmg'), tmp_dir)
    info2 = dmg.info()
    files = file_find.find(tmp_dir, relative = True, file_type = file_find.FILE_OR_LINK)
    self.assertEqual( [ 'foo.txt', 'link_to_foo.txt', 'subdir/bar.txt' ], files )
    #self.assertEqual( info1, info2 )

  def _tmp_example_dmg(self, filename):
    return self._make_test_dmg()

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

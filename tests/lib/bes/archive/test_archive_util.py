#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.archive.archive_util import archive_util
from bes.archive.archiver import archiver
from bes.archive.temp_archive import temp_archive

class test_archive_util(unit_test):

  def test_remove_members(self):
    items = temp_archive.make_temp_item_list([
      ( self.xp_path('foo-1.2.3/fruits/apple.txt'), 'apple.txt' ),
      ( self.xp_path('foo-1.2.3/fruits/durian.txt'), 'durian.txt' ),
      ( self.xp_path('foo-1.2.3/fruits/kiwi.txt'), 'kiwi.txt' ),
      ( self.xp_path('foo-1.2.3/.import/foo.txt'), 'foo.txt' ),
      ( self.xp_path('foo-1.2.3/.import/bar.txt'), 'bar.txt' ),
    ])
    tmp_archive = temp_archive.make_temp_archive(items, 'zip', delete = not self.DEBUG)
    self.assertEqual( [
      'foo-1.2.3/.import/bar.txt',
      'foo-1.2.3/.import/foo.txt',
      'foo-1.2.3/fruits/apple.txt',
      'foo-1.2.3/fruits/durian.txt',
      'foo-1.2.3/fruits/kiwi.txt',
    ], archiver.members(tmp_archive))
    archive_util.remove_members(tmp_archive, [ 'foo-1.2.3/.import' ], debug = True)
    self.assertEqual( [
      'foo-1.2.3/fruits/apple.txt',
      'foo-1.2.3/fruits/durian.txt',
      'foo-1.2.3/fruits/kiwi.txt',
    ], archiver.members(tmp_archive))
    
if __name__ == "__main__":
  unit_test.main()

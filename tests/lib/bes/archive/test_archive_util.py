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
    archive_util.remove_members(tmp_archive, [ 'foo-1.2.3/.import' ], debug = self.DEBUG)
    self.assertEqual( [
      'foo-1.2.3/fruits/apple.txt',
      'foo-1.2.3/fruits/durian.txt',
      'foo-1.2.3/fruits/kiwi.txt',
    ], archiver.members(tmp_archive))

  def test_member_checksums(self):
    a = temp_archive.make_temp_archive(temp_archive.make_temp_item_list([
      ( self.xp_path('foo-1.2.3/fruits/apple.txt'), 'apple.txt' ),
      ( self.xp_path('foo-1.2.3/fruits/durian.txt'), 'durian.txt' ),
      ( self.xp_path('foo-1.2.3/fruits/kiwi.txt'), 'kiwi.txt' ),
    ]), 'zip', delete = not self.DEBUG)
    self.assertEqual( {
      'foo-1.2.3/fruits/apple.txt': '7269b27861e2a5ba6947b6279bb5e66b23439d83a65a3c0cf529f5834ed2e7fb',
      'foo-1.2.3/fruits/kiwi.txt': 'a7be44d9dda7e951298316b34ce84a1b2da8b5e0bead26118145bda4fbca9329',
    }, archive_util.member_checksums(a, [ 'foo-1.2.3/fruits/apple.txt', 'foo-1.2.3/fruits/kiwi.txt' ]) )
    
  def test_duplicate_members(self):
    a1 = temp_archive.make_temp_archive(temp_archive.make_temp_item_list([
      ( self.xp_path('foo-1.2.3/fruits/apple.txt'), 'apple.txt' ),
      ( self.xp_path('foo-1.2.3/fruits/durian.txt'), 'durian.txt' ),
      ( self.xp_path('foo-1.2.3/fruits/kiwi.txt'), 'kiwi.txt' ),
    ]), 'zip', delete = not self.DEBUG, prefix = 'a1-')
    a2 = temp_archive.make_temp_archive(temp_archive.make_temp_item_list([
      ( self.xp_path('foo-1.2.3/fruits/apple.txt'), 'apple.txt' ),
      ( self.xp_path('foo-1.2.3/fruits/lemon.txt'), 'lemon.txt' ),
      ( self.xp_path('foo-1.2.3/fruits/melon.txt'), 'melon.txt' ),
      ( self.xp_path('foo-1.2.3/wine/barolo.txt'), 'barolo.txt' ),
      ( self.xp_path('foo-1.2.3/cheese/brie.txt'), 'brie.txt' ),
    ]), 'zip', delete = not self.DEBUG, prefix = 'a2-')
    a3 = temp_archive.make_temp_archive(temp_archive.make_temp_item_list([
      ( self.xp_path('foo-1.2.3/fruits/strawberry.txt'), 'strawberry.txt' ),
      ( self.xp_path('foo-1.2.3/fruits/blueberry.txt'), 'blueberry.txt' ),
      ( self.xp_path('foo-1.2.3/fruits/banana.txt'), 'banana.txt' ),
      ( self.xp_path('foo-1.2.3/wine/barolo.txt'), 'barolo.txt' ),
      ( self.xp_path('foo-1.2.3/cheese/brie.txt'), 'brie.txt' ),
    ]), 'zip', delete = not self.DEBUG, prefix = 'a3-')
    self.assertEqual( {
      'foo-1.2.3/cheese/brie.txt': { a2, a3 },
      'foo-1.2.3/fruits/apple.txt': { a1, a2 },
      'foo-1.2.3/wine/barolo.txt': { a2, a3 },
    }, archive_util.duplicate_members([ a1, a2, a3 ]) )

  def test_duplicate_members_with_conflicts(self):
    a1 = temp_archive.make_temp_archive(temp_archive.make_temp_item_list([
      ( self.xp_path('foo-1.2.3/fruits/apple.txt'), 'apple.txt' ),
      ( self.xp_path('foo-1.2.3/fruits/durian.txt'), 'durian.txt' ),
      ( self.xp_path('foo-1.2.3/fruits/kiwi.txt'), 'kiwi.txt' ),
    ]), 'zip', delete = not self.DEBUG, prefix = 'a1-')
    a2 = temp_archive.make_temp_archive(temp_archive.make_temp_item_list([
      ( self.xp_path('foo-1.2.3/fruits/apple.txt'), 'apple2.txt' ),
      ( self.xp_path('foo-1.2.3/fruits/durian.txt'), 'durian.txt' ),
      ( self.xp_path('foo-1.2.3/fruits/melon.txt'), 'melon.txt' ),
      ( self.xp_path('foo-1.2.3/wine/barolo.txt'), 'barolo.txt' ),
      ( self.xp_path('foo-1.2.3/cheese/brie.txt'), 'brie.txt' ),
    ]), 'zip', delete = not self.DEBUG, prefix = 'a2-')
    a3 = temp_archive.make_temp_archive(temp_archive.make_temp_item_list([
      ( self.xp_path('foo-1.2.3/fruits/strawberry.txt'), 'strawberry.txt' ),
      ( self.xp_path('foo-1.2.3/fruits/blueberry.txt'), 'blueberry.txt' ),
      ( self.xp_path('foo-1.2.3/fruits/banana.txt'), 'banana.txt' ),
      ( self.xp_path('foo-1.2.3/wine/barolo.txt'), 'barolo.txt' ),
      ( self.xp_path('foo-1.2.3/cheese/brie.txt'), 'brie2.txt' ),
    ]), 'zip', delete = not self.DEBUG, prefix = 'a3-')
    self.assertEqual( {
      'foo-1.2.3/cheese/brie.txt': { a2, a3 },
      'foo-1.2.3/fruits/apple.txt': { a1, a2 },
    }, archive_util.duplicate_members([ a1, a2, a3 ], only_content_conficts = True) )

  def test_combine(self):
    a1 = temp_archive.make_temp_archive(temp_archive.make_temp_item_list([
      ( self.xp_path('fruits/apple.txt'), 'apple.txt' ),
      ( self.xp_path('fruits/durian.txt'), 'durian.txt' ),
      ( self.xp_path('fruits/kiwi.txt'), 'kiwi.txt' ),
    ]), 'zip', delete = not self.DEBUG, prefix = 'a1-')
    a2 = temp_archive.make_temp_archive(temp_archive.make_temp_item_list([
      ( self.xp_path('fruits/melon.txt'), 'melon.txt' ),
      ( self.xp_path('fruits/lemon.txt'), 'lemon.txt' ),
      ( self.xp_path('fruits/dragonfruit.txt'), 'dragonfruit.txt' ),
    ]), 'zip', delete = not self.DEBUG, prefix = 'a2-')
    a3 = temp_archive.make_temp_archive(temp_archive.make_temp_item_list([
      ( self.xp_path('fruits/strawberry.txt'), 'strawberry.txt' ),
      ( self.xp_path('fruits/pear.txt'), 'pear.txt' ),
      ( self.xp_path('fruits/plum.txt'), 'plum.txt' ),
    ]), 'zip', delete = not self.DEBUG, prefix = 'a3-')
    tmp_archive = self.make_temp_file(suffix = '.zip')
    archive_util.combine([ a1, a2, a3 ], tmp_archive)
    self.assertEqual( [
      self.xp_path('fruits/apple.txt'),
      self.xp_path('fruits/dragonfruit.txt'),
      self.xp_path('fruits/durian.txt'),
      self.xp_path('fruits/kiwi.txt'),
      self.xp_path('fruits/lemon.txt'),
      self.xp_path('fruits/melon.txt'),
      self.xp_path('fruits/pear.txt'),
      self.xp_path('fruits/plum.txt'),
      self.xp_path('fruits/strawberry.txt'),
    ], archiver.members(tmp_archive) )

if __name__ == "__main__":
  unit_test.main()

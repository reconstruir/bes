#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.archive.archive_util import archive_util
from bes.archive.archiver import archiver
from bes.archive.temp_archive import temp_archive

class test_archive_util(unit_test):

  def test_remove_members(self):
    items = temp_archive.make_temp_item_list([
      ( self.native_filename('foo-1.2.3/fruits/apple.txt'), 'apple.txt' ),
      ( self.native_filename('foo-1.2.3/fruits/durian.txt'), 'durian.txt' ),
      ( self.native_filename('foo-1.2.3/fruits/kiwi.txt'), 'kiwi.txt' ),
      ( self.native_filename('foo-1.2.3/.import/foo.txt'), 'foo.txt' ),
      ( self.native_filename('foo-1.2.3/.import/bar.txt'), 'bar.txt' ),
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
      ( self.native_filename('foo-1.2.3/fruits/apple.txt'), 'apple.txt' ),
      ( self.native_filename('foo-1.2.3/fruits/durian.txt'), 'durian.txt' ),
      ( self.native_filename('foo-1.2.3/fruits/kiwi.txt'), 'kiwi.txt' ),
    ]), 'zip', delete = not self.DEBUG)
    self.assertEqual( {
      'foo-1.2.3/fruits/apple.txt': '7269b27861e2a5ba6947b6279bb5e66b23439d83a65a3c0cf529f5834ed2e7fb',
      'foo-1.2.3/fruits/kiwi.txt': 'a7be44d9dda7e951298316b34ce84a1b2da8b5e0bead26118145bda4fbca9329',
    }, archive_util.member_checksums(a, [ 'foo-1.2.3/fruits/apple.txt', 'foo-1.2.3/fruits/kiwi.txt' ]) )
    
  def test_duplicate_members(self):
    a1 = temp_archive.make_temp_archive(temp_archive.make_temp_item_list([
      ( self.native_filename('foo-1.2.3/fruits/apple.txt'), 'apple.txt' ),
      ( self.native_filename('foo-1.2.3/fruits/durian.txt'), 'durian.txt' ),
      ( self.native_filename('foo-1.2.3/fruits/kiwi.txt'), 'kiwi.txt' ),
    ]), 'zip', delete = not self.DEBUG, prefix = 'a1-')
    a2 = temp_archive.make_temp_archive(temp_archive.make_temp_item_list([
      ( self.native_filename('foo-1.2.3/fruits/apple.txt'), 'apple.txt' ),
      ( self.native_filename('foo-1.2.3/fruits/lemon.txt'), 'lemon.txt' ),
      ( self.native_filename('foo-1.2.3/fruits/melon.txt'), 'melon.txt' ),
      ( self.native_filename('foo-1.2.3/wine/barolo.txt'), 'barolo.txt' ),
      ( self.native_filename('foo-1.2.3/cheese/brie.txt'), 'brie.txt' ),
    ]), 'zip', delete = not self.DEBUG, prefix = 'a2-')
    a3 = temp_archive.make_temp_archive(temp_archive.make_temp_item_list([
      ( self.native_filename('foo-1.2.3/fruits/strawberry.txt'), 'strawberry.txt' ),
      ( self.native_filename('foo-1.2.3/fruits/blueberry.txt'), 'blueberry.txt' ),
      ( self.native_filename('foo-1.2.3/fruits/banana.txt'), 'banana.txt' ),
      ( self.native_filename('foo-1.2.3/wine/barolo.txt'), 'barolo.txt' ),
      ( self.native_filename('foo-1.2.3/cheese/brie.txt'), 'brie.txt' ),
    ]), 'zip', delete = not self.DEBUG, prefix = 'a3-')
    self.assertEqual( {
      'foo-1.2.3/cheese/brie.txt': { a2, a3 },
      'foo-1.2.3/fruits/apple.txt': { a1, a2 },
      'foo-1.2.3/wine/barolo.txt': { a2, a3 },
    }, archive_util.duplicate_members([ a1, a2, a3 ]) )

  def test_duplicate_members_with_conflicts(self):
    a1 = temp_archive.make_temp_archive(temp_archive.make_temp_item_list([
      ( self.native_filename('foo-1.2.3/fruits/apple.txt'), 'apple.txt' ),
      ( self.native_filename('foo-1.2.3/fruits/durian.txt'), 'durian.txt' ),
      ( self.native_filename('foo-1.2.3/fruits/kiwi.txt'), 'kiwi.txt' ),
    ]), 'zip', delete = not self.DEBUG, prefix = 'a1-')
    a2 = temp_archive.make_temp_archive(temp_archive.make_temp_item_list([
      ( self.native_filename('foo-1.2.3/fruits/apple.txt'), 'apple2.txt' ),
      ( self.native_filename('foo-1.2.3/fruits/durian.txt'), 'durian.txt' ),
      ( self.native_filename('foo-1.2.3/fruits/melon.txt'), 'melon.txt' ),
      ( self.native_filename('foo-1.2.3/wine/barolo.txt'), 'barolo.txt' ),
      ( self.native_filename('foo-1.2.3/cheese/brie.txt'), 'brie.txt' ),
    ]), 'zip', delete = not self.DEBUG, prefix = 'a2-')
    a3 = temp_archive.make_temp_archive(temp_archive.make_temp_item_list([
      ( self.native_filename('foo-1.2.3/fruits/strawberry.txt'), 'strawberry.txt' ),
      ( self.native_filename('foo-1.2.3/fruits/blueberry.txt'), 'blueberry.txt' ),
      ( self.native_filename('foo-1.2.3/fruits/banana.txt'), 'banana.txt' ),
      ( self.native_filename('foo-1.2.3/wine/barolo.txt'), 'barolo.txt' ),
      ( self.native_filename('foo-1.2.3/cheese/brie.txt'), 'brie2.txt' ),
    ]), 'zip', delete = not self.DEBUG, prefix = 'a3-')
    self.assertEqual( {
      'foo-1.2.3/cheese/brie.txt': { a2, a3 },
      'foo-1.2.3/fruits/apple.txt': { a1, a2 },
    }, archive_util.duplicate_members([ a1, a2, a3 ], only_content_conficts = True) )

  def test_combine(self):
    a1 = temp_archive.make_temp_archive(temp_archive.make_temp_item_list([
      ( self.native_filename('fruits/apple.txt'), 'apple.txt' ),
      ( self.native_filename('fruits/durian.txt'), 'durian.txt' ),
      ( self.native_filename('fruits/kiwi.txt'), 'kiwi.txt' ),
    ]), 'zip', delete = not self.DEBUG, prefix = 'a1-')
    a2 = temp_archive.make_temp_archive(temp_archive.make_temp_item_list([
      ( self.native_filename('fruits/melon.txt'), 'melon.txt' ),
      ( self.native_filename('fruits/lemon.txt'), 'lemon.txt' ),
      ( self.native_filename('fruits/dragonfruit.txt'), 'dragonfruit.txt' ),
    ]), 'zip', delete = not self.DEBUG, prefix = 'a2-')
    a3 = temp_archive.make_temp_archive(temp_archive.make_temp_item_list([
      ( self.native_filename('fruits/strawberry.txt'), 'strawberry.txt' ),
      ( self.native_filename('fruits/pear.txt'), 'pear.txt' ),
      ( self.native_filename('fruits/plum.txt'), 'plum.txt' ),
    ]), 'zip', delete = not self.DEBUG, prefix = 'a3-')
    tmp_archive = self.make_temp_file(suffix = '.zip')
    archive_util.combine([ a1, a2, a3 ], tmp_archive)
    self.assertEqual( [
      'fruits/apple.txt',
      'fruits/dragonfruit.txt',
      'fruits/durian.txt',
      'fruits/kiwi.txt',
      'fruits/lemon.txt',
      'fruits/melon.txt',
      'fruits/pear.txt',
      'fruits/plum.txt',
      'fruits/strawberry.txt',
    ], archiver.members(tmp_archive) )

  def test_combine_conflicts_same_content(self):
    a1 = temp_archive.make_temp_archive(temp_archive.make_temp_item_list([
      ( self.native_filename('fruits/apple.txt'), 'apple.txt' ),
      ( self.native_filename('fruits/durian.txt'), 'durian.txt' ),
      ( self.native_filename('fruits/kiwi.txt'), 'kiwi.txt' ),
      ( self.native_filename('fruits/plum.txt'), 'plum.txt' ),
    ]), 'zip', delete = not self.DEBUG, prefix = 'a1-')
    a2 = temp_archive.make_temp_archive(temp_archive.make_temp_item_list([
      ( self.native_filename('fruits/kiwi.txt'), 'kiwi.txt' ),
      ( self.native_filename('fruits/melon.txt'), 'melon.txt' ),
      ( self.native_filename('fruits/lemon.txt'), 'lemon.txt' ),
      ( self.native_filename('fruits/dragonfruit.txt'), 'dragonfruit.txt' ),
    ]), 'zip', delete = not self.DEBUG, prefix = 'a2-')
    a3 = temp_archive.make_temp_archive(temp_archive.make_temp_item_list([
      ( self.native_filename('fruits/lemon.txt'), 'lemon.txt' ),
      ( self.native_filename('fruits/strawberry.txt'), 'strawberry.txt' ),
      ( self.native_filename('fruits/pear.txt'), 'pear.txt' ),
      ( self.native_filename('fruits/plum.txt'), 'plum.txt' ),
    ]), 'zip', delete = not self.DEBUG, prefix = 'a3-')
    tmp_archive = self.make_temp_file(suffix = '.zip')
    archive_util.combine([ a1, a2, a3 ], tmp_archive)
    self.assertEqual( [
      'fruits/apple.txt',
      'fruits/dragonfruit.txt',
      'fruits/durian.txt',
      'fruits/kiwi.txt',
      'fruits/lemon.txt',
      'fruits/melon.txt',
      'fruits/pear.txt',
      'fruits/plum.txt',
      'fruits/strawberry.txt',
    ], archiver.members(tmp_archive) )

  def test_combine_conflicts_different_content_no_check(self):
    a1 = temp_archive.make_temp_archive(temp_archive.make_temp_item_list([
      ( self.native_filename('fruits/apple.txt'), 'apple.txt' ),
      ( self.native_filename('fruits/durian.txt'), 'durian.txt' ),
      ( self.native_filename('fruits/kiwi.txt'), 'kiwi.txt' ),
      ( self.native_filename('fruits/plum.txt'), '1plum.txt' ),
    ]), 'zip', delete = not self.DEBUG, prefix = 'a1-')
    a2 = temp_archive.make_temp_archive(temp_archive.make_temp_item_list([
      ( self.native_filename('fruits/kiwi.txt'), 'kiwi.txt' ),
      ( self.native_filename('fruits/melon.txt'), 'melon.txt' ),
      ( self.native_filename('fruits/lemon.txt'), '1lemon.txt' ),
      ( self.native_filename('fruits/dragonfruit.txt'), 'dragonfruit.txt' ),
    ]), 'zip', delete = not self.DEBUG, prefix = 'a2-')
    a3 = temp_archive.make_temp_archive(temp_archive.make_temp_item_list([
      ( self.native_filename('fruits/lemon.txt'), '2lemon.txt' ),
      ( self.native_filename('fruits/strawberry.txt'), 'strawberry.txt' ),
      ( self.native_filename('fruits/pear.txt'), 'pear.txt' ),
      ( self.native_filename('fruits/plum.txt'), '2plum.txt' ),
    ]), 'zip', delete = not self.DEBUG, prefix = 'a3-')
    tmp_archive = self.make_temp_file(suffix = '.zip')
    archive_util.combine([ a1, a2, a3 ], tmp_archive)
    self.assertEqual( [
      'fruits/apple.txt',
      'fruits/dragonfruit.txt',
      'fruits/durian.txt',
      'fruits/kiwi.txt',
      'fruits/lemon.txt',
      'fruits/melon.txt',
      'fruits/pear.txt',
      'fruits/plum.txt',
      'fruits/strawberry.txt',
    ], archiver.members(tmp_archive) )

  def test_combine_conflicts_different_content_with_check(self):
    a1 = temp_archive.make_temp_archive(temp_archive.make_temp_item_list([
      ( self.native_filename('fruits/apple.txt'), 'apple.txt' ),
      ( self.native_filename('fruits/durian.txt'), 'durian.txt' ),
      ( self.native_filename('fruits/kiwi.txt'), 'kiwi.txt' ),
      ( self.native_filename('fruits/plum.txt'), '1plum.txt' ),
    ]), 'zip', delete = not self.DEBUG, prefix = 'a1-')
    a2 = temp_archive.make_temp_archive(temp_archive.make_temp_item_list([
      ( self.native_filename('fruits/kiwi.txt'), 'kiwi.txt' ),
      ( self.native_filename('fruits/melon.txt'), 'melon.txt' ),
      ( self.native_filename('fruits/lemon.txt'), '1lemon.txt' ),
      ( self.native_filename('fruits/dragonfruit.txt'), 'dragonfruit.txt' ),
    ]), 'zip', delete = not self.DEBUG, prefix = 'a2-')
    a3 = temp_archive.make_temp_archive(temp_archive.make_temp_item_list([
      ( self.native_filename('fruits/lemon.txt'), '2lemon.txt' ),
      ( self.native_filename('fruits/strawberry.txt'), 'strawberry.txt' ),
      ( self.native_filename('fruits/pear.txt'), 'pear.txt' ),
      ( self.native_filename('fruits/plum.txt'), '2plum.txt' ),
    ]), 'zip', delete = not self.DEBUG, prefix = 'a3-')
    tmp_archive = self.make_temp_file(suffix = '.zip')
    with self.assertRaises(RuntimeError) as ctx:
      archive_util.combine([ a1, a2, a3 ], tmp_archive, check_content = True)

  def test_combine_with_base_dir(self):
    a1 = temp_archive.make_temp_archive(temp_archive.make_temp_item_list([
      ( self.native_filename('fruits/apple.txt'), 'apple.txt' ),
      ( self.native_filename('fruits/durian.txt'), 'durian.txt' ),
      ( self.native_filename('fruits/kiwi.txt'), 'kiwi.txt' ),
    ]), 'zip', delete = not self.DEBUG, prefix = 'a1-')
    a2 = temp_archive.make_temp_archive(temp_archive.make_temp_item_list([
      ( self.native_filename('fruits/melon.txt'), 'melon.txt' ),
      ( self.native_filename('fruits/lemon.txt'), 'lemon.txt' ),
      ( self.native_filename('fruits/dragonfruit.txt'), 'dragonfruit.txt' ),
    ]), 'zip', delete = not self.DEBUG, prefix = 'a2-')
    a3 = temp_archive.make_temp_archive(temp_archive.make_temp_item_list([
      ( self.native_filename('fruits/strawberry.txt'), 'strawberry.txt' ),
      ( self.native_filename('fruits/pear.txt'), 'pear.txt' ),
      ( self.native_filename('fruits/plum.txt'), 'plum.txt' ),
    ]), 'zip', delete = not self.DEBUG, prefix = 'a3-')
    tmp_archive = self.make_temp_file(suffix = '.zip')
    archive_util.combine([ a1, a2, a3 ], tmp_archive, base_dir = 'foo-1.2.3')
    self.assertEqual( [
      'foo-1.2.3/fruits/apple.txt',
      'foo-1.2.3/fruits/dragonfruit.txt',
      'foo-1.2.3/fruits/durian.txt',
      'foo-1.2.3/fruits/kiwi.txt',
      'foo-1.2.3/fruits/lemon.txt',
      'foo-1.2.3/fruits/melon.txt',
      'foo-1.2.3/fruits/pear.txt',
      'foo-1.2.3/fruits/plum.txt',
      'foo-1.2.3/fruits/strawberry.txt',
    ], archiver.members(tmp_archive) )

  def test_combine_conflicts_different_content_with_check_and_exclude(self):
    a1 = temp_archive.make_temp_archive(temp_archive.make_temp_item_list([
      ( self.native_filename('fruits/apple.txt'), 'apple.txt' ),
      ( self.native_filename('fruits/durian.txt'), 'durian.txt' ),
      ( self.native_filename('fruits/plum.txt'), '1plum.txt' ),
    ]), 'zip', delete = not self.DEBUG, prefix = 'a1-')
    a2 = temp_archive.make_temp_archive(temp_archive.make_temp_item_list([
      ( self.native_filename('fruits/kiwi.txt'), 'kiwi.txt' ),
      ( self.native_filename('fruits/melon.txt'), 'melon.txt' ),
      ( self.native_filename('fruits/plum.txt'), '2plum.txt' ),
    ]), 'zip', delete = not self.DEBUG, prefix = 'a2-')
    a3 = temp_archive.make_temp_archive(temp_archive.make_temp_item_list([
      ( self.native_filename('fruits/lemon.txt'), 'lemon.txt' ),
      ( self.native_filename('fruits/strawberry.txt'), 'strawberry.txt' ),
      ( self.native_filename('fruits/plum.txt'), '3plum.txt' ),
    ]), 'zip', delete = not self.DEBUG, prefix = 'a3-')
    tmp_archive = self.make_temp_file(suffix = '.zip')
    archive_util.combine([ a1, a2, a3 ], tmp_archive, check_content = True, exclude = [ 'fruits/plum.txt' ])
    self.assertEqual( [
      'fruits/apple.txt',
      'fruits/durian.txt',
      'fruits/kiwi.txt',
      'fruits/lemon.txt',
      'fruits/melon.txt',
      'fruits/strawberry.txt',
    ], archiver.members(tmp_archive) )
    
  def test_match_members(self):
    tmp_archive = temp_archive.make_temp_archive(temp_archive.make_temp_item_list([
      ( self.native_filename('fruits/apple.pdf'), 'apple.pdf' ),
      ( self.native_filename('fruits/durian.pdf'), 'durian.pdf' ),
      ( self.native_filename('fruits/plum.pdf'), 'plum.pdf' ),
      ( self.native_filename('cheese/brie.txt'), 'brie.txt' ),
      ( self.native_filename('cheese/cheddar.txt'), 'cheddar.txt' ),
      ( self.native_filename('cheese/fontina.txt'), 'fontina.txt' ),
    ]), 'zip', delete = not self.DEBUG)
    self.assertEqual( [
      'cheese/brie.txt',
      'cheese/cheddar.txt',
      'cheese/fontina.txt',
      'fruits/apple.pdf',
      'fruits/durian.pdf',
      'fruits/plum.pdf',
    ], archive_util.match_members(tmp_archive, [ '*' ]) )
    self.assertEqual( [
      'cheese/brie.txt',
      'cheese/cheddar.txt',
      'cheese/fontina.txt',
    ], archive_util.match_members(tmp_archive, [ 'cheese*' ]) )
    self.assertEqual( [
      'cheese/brie.txt',
      'cheese/cheddar.txt',
      'cheese/fontina.txt',
    ], archive_util.match_members(tmp_archive, [ '*.txt' ]) )
    self.assertEqual( [
      'fruits/apple.pdf',
      'fruits/durian.pdf',
      'fruits/plum.pdf',
    ], archive_util.match_members(tmp_archive, [ '*.pdf' ]) )

  def test_remove_members_matching_patterns(self):
    items = temp_archive.make_temp_item_list([
      ( self.native_filename('foo-1.2.3/fruits/apple.txt'), 'apple.txt' ),
      ( self.native_filename('foo-1.2.3/fruits/durian.txt'), 'durian.txt' ),
      ( self.native_filename('foo-1.2.3/fruits/kiwi.txt'), 'kiwi.txt' ),
      ( self.native_filename('foo-1.2.3/.import/foo.txt'), 'foo.txt' ),
      ( self.native_filename('foo-1.2.3/.import/bar.txt'), 'bar.txt' ),
      ( self.native_filename('foo-1.2.3/cheese/brie.jpg'), 'brie.jpg' ),
      ( self.native_filename('foo-1.2.3/cheese/halumi.jpg'), 'halumi.jpg' ),
      ( self.native_filename('foo-1.2.3/cheese/feta.jpg'), 'feta.jpg' ),
    ])
    tmp_archive = temp_archive.make_temp_archive(items, 'zip', delete = not self.DEBUG)
    archive_util.remove_members_matching_patterns(tmp_archive, [ 'notfound' ], debug = self.DEBUG)
    self.assertEqual( [
      'foo-1.2.3/.import/bar.txt',
      'foo-1.2.3/.import/foo.txt',
      'foo-1.2.3/cheese/brie.jpg',
      'foo-1.2.3/cheese/feta.jpg',
      'foo-1.2.3/cheese/halumi.jpg',
      'foo-1.2.3/fruits/apple.txt',
      'foo-1.2.3/fruits/durian.txt',
      'foo-1.2.3/fruits/kiwi.txt',
    ], archiver.members(tmp_archive))

    tmp_archive = temp_archive.make_temp_archive(items, 'zip', delete = not self.DEBUG)
    archive_util.remove_members_matching_patterns(tmp_archive, [ '*.txt' ], debug = self.DEBUG)
    self.assertEqual( [
      'foo-1.2.3/cheese/brie.jpg',
      'foo-1.2.3/cheese/feta.jpg',
      'foo-1.2.3/cheese/halumi.jpg',
    ], archiver.members(tmp_archive))

    tmp_archive = temp_archive.make_temp_archive(items, 'zip', delete = not self.DEBUG)
    archive_util.remove_members_matching_patterns(tmp_archive, [ '*cheese*' ], debug = self.DEBUG)
    self.assertEqual( [
      'foo-1.2.3/.import/bar.txt',
      'foo-1.2.3/.import/foo.txt',
      'foo-1.2.3/fruits/apple.txt',
      'foo-1.2.3/fruits/durian.txt',
      'foo-1.2.3/fruits/kiwi.txt',
    ], archiver.members(tmp_archive))

  def test_read_patterns(self):
    content = '''\
cheese.txt
foo.jpg
test_orange/foo.txt
test_kiwi/*
'''
    tmp_file = self.make_temp_file(content = content)
    self.assertEqual( [
      'cheese.txt',
      'foo.jpg',
      'test_orange/foo.txt',
      'test_kiwi/*',
    ], archive_util.read_patterns(tmp_file) )
    
if __name__ == "__main__":
  unit_test.main()

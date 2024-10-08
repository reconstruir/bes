#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, os.path as path

from bes.testing.unit_test import unit_test
from bes.archive.temp_archive import temp_archive
from bes.system.check import check
from bes.fs.file_find import file_find
from bes.fs.file_util import file_util
from bes.match.matcher_always_false import matcher_always_false
from bes.match.matcher_always_true import matcher_always_true
from bes.match.matcher_filename import matcher_multiple_filename

def make_test_case(archive_class, xarchive_type):

  class _archive_test_case(unit_test):
    'Helper that implements the logic for a lot of archive tests.'
  
    def make_archive(self, filename):
      check.check_string(filename)
      archive = archive_class(filename)
      if self.DEBUG:
        print('archive: {}'.format(archive.filename))
      return archive
    
    def make_temp_archive_for_reading(self, items, archive_type = None):
      archive_type = archive_type or xarchive_type
      assert archive_type
      tmp_archive = temp_archive.make_temp_archive(items, archive_type, delete = not self.DEBUG)
      return self.make_archive(tmp_archive)
  
    def make_temp_archive_for_writing(self):
      tmp_archive = self.make_temp_file(suffix = '.' + xarchive_type)
      return self.make_archive(tmp_archive)
  
    def test_members(self):
      assert xarchive_type
      tmp_tar = temp_archive.make_temp_archive([ temp_archive.item('foo.txt', content = 'foo.txt\n') ],
                                               xarchive_type,
                                               delete = not self.DEBUG)
      self.assertEqual( [ 'foo.txt' ], self.make_archive(tmp_tar).members )
  
    def test_has_member(self):
      items = temp_archive.make_temp_item_list([
        ( self.native_filename('foo/apple.txt'), 'apple.txt\n' ),
        ( self.native_filename('foo/durian.txt'), 'durian.txt\n' ),
        ( self.native_filename('foo/kiwi.txt'), 'kiwi.txt\n' ),
        ( self.native_filename('metadata/db.json'), '{}\n' ),
      ])
      tmp_archive = self.make_temp_archive_for_reading(items)
      self.assertTrue( self.make_archive(tmp_archive.filename).has_member('foo/apple.txt') )
      self.assertFalse( self.make_archive(tmp_archive.filename).has_member('nothere.txt') )
  
    def test_extract_all(self):
      items = temp_archive.make_temp_item_list([
        ( self.native_filename('foo.txt'), 'foo.txt\n' ),
      ])
      tmp_archive = self.make_temp_archive_for_reading(items)
      tmp_dir = self.make_temp_dir()
      tmp_archive.extract_all(tmp_dir)
      self.assertTrue( path.isfile(path.join(tmp_dir, self.native_filename('foo.txt'))) )
  
    def test_extract_all_with_base_dir(self):
      items = temp_archive.make_temp_item_list([
        ( self.native_filename('foo.txt'), 'foo.txt\n' ),
      ])
      tmp_archive = self.make_temp_archive_for_reading(items)
      tmp_dir = self.make_temp_dir()
      base_dir = self.native_filename('base-1.2.3')
      tmp_archive.extract_all(tmp_dir, base_dir = base_dir)
      self.assertTrue( path.isfile(path.join(tmp_dir, base_dir, self.native_filename('foo.txt'))) )
  
    def test_extract_all_with_strip_common_ancestor(self):
      base_dir_to_strip = self.native_filename('base-1.2.3')
      items = temp_archive.make_temp_item_list([
        ( self.native_filename('foo.txt'), 'foo.txt\n' ),
      ])
      items = temp_archive.add_base_dir(items, base_dir_to_strip)
      tmp_archive = self.make_temp_archive_for_reading(items)
      tmp_dir = self.make_temp_dir()
      tmp_archive.extract_all(tmp_dir, strip_common_ancestor = True)
      self.assertTrue( path.isfile(path.join(tmp_dir, self.native_filename('foo.txt'))) )
  
    def test_extract_all_with_base_dir_and_strip_common_ancestor(self):
      base_dir_to_strip = self.native_filename('base-1.2.3')
      items = temp_archive.make_temp_item_list([
        ( self.native_filename('foo.txt'), 'foo.txt\n' ),
      ])
      items = temp_archive.add_base_dir(items, base_dir_to_strip)
      base_dir_to_add = self.native_filename('added-6.6.6')
      tmp_archive = self.make_temp_archive_for_reading(items)
      tmp_dir = self.make_temp_dir()
      tmp_archive.extract_all(tmp_dir, base_dir = base_dir_to_add, strip_common_ancestor = True)
      self.assertTrue( path.isfile(path.join(tmp_dir, base_dir_to_add, self.native_filename('foo.txt'))) )
  
    def test_extract_all_with_strip_head(self):
  
      items = temp_archive.make_temp_item_list([
        ( self.native_filename('foo/apple.txt'), 'apple.txt\n' ),
        ( self.native_filename('foo/durian.txt'), 'durian.txt\n' ),
        ( self.native_filename('foo/kiwi.txt'), 'kiwi.txt\n' ),
        ( self.native_filename('metadata/db.json'), '{}\n' ),
      ])
      tmp_archive = self.make_temp_archive_for_reading(items)
      tmp_dir = self.make_temp_dir()
      tmp_archive.extract_all(tmp_dir, strip_head = self.native_filename('foo'))
  
      actual_files = file_find.find(tmp_dir, relative = True)
      for f in actual_files:
        print(f'FILE: {f}')
  
      expected_files = [
        self.native_filename('apple.txt'),
        self.native_filename('durian.txt'),
        self.native_filename('kiwi.txt'),
        self.native_filename('metadata/db.json'),
      ]
  
      self.assertEqual( expected_files, actual_files )
  
    def test_extract_all_with_strip_common_ancestor_and_strip_head(self):
  
      items = temp_archive.make_temp_item_list([
        ( self.native_filename('base-1.2.3/foo/apple.txt'), 'apple.txt\n' ),
        ( self.native_filename('base-1.2.3/foo/durian.txt'), 'durian.txt\n' ),
        ( self.native_filename('base-1.2.3/foo/kiwi.txt'), 'kiwi.txt\n' ),
        ( self.native_filename('base-1.2.3/metadata/db.json'), '{}\n' ),
      ])
      tmp_archive = self.make_temp_archive_for_reading(items)
      tmp_dir = self.make_temp_dir()
      tmp_archive.extract_all(tmp_dir, strip_common_ancestor = True, strip_head = self.native_filename('foo'))
  
      actual_files = file_find.find(tmp_dir, relative = True)
  
      expected_files = [
        self.native_filename('apple.txt'),
        self.native_filename('durian.txt'),
        self.native_filename('kiwi.txt'),
        self.native_filename('metadata/db.json'),
      ]
  
      self.assertEqual( expected_files, actual_files )
  
    def test_extract_all_overlap(self):
  
      items1 = temp_archive.make_temp_item_list([
        ( self.native_filename('base-1.2.3/foo.txt'), 'foo.txt\n' ),
        ( self.native_filename('base-1.2.3/bar.txt'), 'bar.txt\n' ),
      ])
  
      items2 = temp_archive.make_temp_item_list([
        ( self.native_filename('base-1.2.3/orange.txt'), 'orange.txt\n' ),
        ( self.native_filename('base-1.2.3/kiwi.txt'), 'kiwi.txt\n' ),
      ])
  
      tmp_archive1 = self.make_temp_archive_for_reading(items1)
      tmp_archive2 = self.make_temp_archive_for_reading(items2)
  
      tmp_dir = self.make_temp_dir()
      tmp_archive1.extract_all(tmp_dir)
      tmp_archive2.extract_all(tmp_dir)
  
      actual_files = file_find.find(tmp_dir, relative = True)
  
      expected_files = [
        self.native_filename('base-1.2.3/bar.txt'),
        self.native_filename('base-1.2.3/foo.txt'),
        self.native_filename('base-1.2.3/kiwi.txt'),
        self.native_filename('base-1.2.3/orange.txt'),
      ]
  
      self.assertEqual( expected_files, actual_files )
  
    def test_extract_all_overlap_with_base_dir(self):
  
      items1 = temp_archive.make_temp_item_list([
        ( self.native_filename('base-1.2.3/foo.txt'), 'foo.txt\n' ),
        ( self.native_filename('base-1.2.3/bar.txt'), 'bar.txt\n' ),
      ])
  
      items2 = temp_archive.make_temp_item_list([
        ( self.native_filename('base-1.2.3/orange.txt'), 'orange.txt\n' ),
        ( self.native_filename('base-1.2.3/kiwi.txt'), 'kiwi.txt\n' ),
      ])
  
      tmp_archive1 = self.make_temp_archive_for_reading(items1)
      tmp_archive2 = self.make_temp_archive_for_reading(items2)
  
      tmp_dir = self.make_temp_dir()
      base_dir = self.native_filename('foo-6.6.6')
      tmp_archive1.extract_all(tmp_dir, base_dir = base_dir)
      tmp_archive2.extract_all(tmp_dir, base_dir = base_dir)
  
      actual_files = file_find.find(tmp_dir, relative = True)
  
      expected_files = [
        self.native_filename('foo-6.6.6/base-1.2.3/bar.txt'),
        self.native_filename('foo-6.6.6/base-1.2.3/foo.txt'),
        self.native_filename('foo-6.6.6/base-1.2.3/kiwi.txt'),
        self.native_filename('foo-6.6.6/base-1.2.3/orange.txt'),
      ]
  
      self.assertEqual( expected_files, actual_files )
  
    def test_extract_all_overlap_with_base_dir_and_strip_common_ancestor(self):
  
      items1 = temp_archive.make_temp_item_list([
        ( self.native_filename('base-1.2.3/foo.txt'), 'foo.txt\n' ),
        ( self.native_filename('base-1.2.3/subdir/bar.txt'), 'bar.txt\n' ),
      ])
  
      items2 = temp_archive.make_temp_item_list([
        ( self.native_filename('notbase-1.2.3/orange.txt'), 'orange.txt\n' ),
        ( self.native_filename('notbase-1.2.3/subdir/kiwi.txt'), 'kiwi.txt\n' ),
      ])
  
      tmp_archive1 = self.make_temp_archive_for_reading(items1)
      tmp_archive2 = self.make_temp_archive_for_reading(items2)
  
      tmp_dir = self.make_temp_dir()
      base_dir = self.native_filename('foo-6.6.6')
      tmp_archive1.extract_all(tmp_dir, base_dir = base_dir, strip_common_ancestor = True)
      tmp_archive2.extract_all(tmp_dir, base_dir = base_dir, strip_common_ancestor = True)
  
      actual_files = file_find.find(tmp_dir, relative = True)
      expected_files = [
        self.native_filename('foo-6.6.6/foo.txt'),
        self.native_filename('foo-6.6.6/orange.txt'),
        self.native_filename('foo-6.6.6/subdir/bar.txt'),
        self.native_filename('foo-6.6.6/subdir/kiwi.txt'),
      ]
      self.assertEqual( expected_files, actual_files )
  
    def test_extract_with_include(self):
      items = temp_archive.make_temp_item_list([
        ( self.native_filename('foo/apple.txt'), 'apple.txt\n' ),
        ( self.native_filename('foo/durian.txt'), 'durian.txt\n' ),
        ( self.native_filename('foo/kiwi.txt'), 'kiwi.txt\n' ),
        ( self.native_filename('metadata/db.json'), '{}\n' ),
      ])
      include = [ self.native_filename('*.txt') ]
      exclude = None
      actual_files = self._test_extract_with_include_exclude(items, include, exclude)
      expected_files = [
        self.native_filename('foo/apple.txt'),
        self.native_filename('foo/durian.txt'),
        self.native_filename('foo/kiwi.txt'),
      ]
      self.assertEqual( expected_files, actual_files )
  
    def test_extract_with_exclude(self):
      items = temp_archive.make_temp_item_list([
        ( self.native_filename('foo/apple.txt'), 'apple.txt\n' ),
        ( self.native_filename('foo/durian.txt'), 'durian.txt\n' ),
        ( self.native_filename('foo/kiwi.txt'), 'kiwi.txt\n' ),
        ( self.native_filename('metadata/db.json'), '{}\n' ),
      ])
      include = None
      exclude = [ self.native_filename('*.txt') ]
      actual_files = self._test_extract_with_include_exclude(items, include, exclude)
      expected_files = [
        self.native_filename('metadata/db.json'),
      ]
      self.assertEqual( expected_files, actual_files )
  
    def test_extract_with_include_and_exclude(self):
      items = temp_archive.make_temp_item_list([
        ( self.native_filename('foo/apple.txt'), 'apple.txt\n' ),
        ( self.native_filename('foo/durian.txt'), 'durian.txt\n' ),
        ( self.native_filename('foo/kiwi.txt'), 'kiwi.txt\n' ),
        ( self.native_filename('metadata/db.json'), '{}\n' ),
      ])
      include = [ '*.txt' ]
      exclude = [ '*durian*' ]
      actual_files = self._test_extract_with_include_exclude(items, include, exclude)
  
      expected_files = [
        self.native_filename('foo/apple.txt'),
        self.native_filename('foo/kiwi.txt'),
      ]
      self.assertEqual( expected_files, actual_files )
  
    def _test_extract_with_include_exclude(self, items, include, exclude):
      tmp_archive = self.make_temp_archive_for_reading(items)
      tmp_dir = self.make_temp_dir()
      tmp_archive.extract(tmp_dir, include = include, exclude = exclude)
      actual_files = file_find.find(tmp_dir, relative = True)
      file_util.remove(tmp_dir)
      return actual_files
  
    def test_extract_member_to_string(self):
      items = temp_archive.make_temp_item_list([
        ( self.native_filename('foo/apple.txt'), 'apple.txt\n' ),
        ( self.native_filename('foo/durian.txt'), 'durian.txt\n' ),
        ( self.native_filename('foo/kiwi.txt'), 'kiwi.txt\n' ),
        ( self.native_filename('metadata/db.json'), '{}\n' ),
      ])
      tmp_archive = self.make_temp_archive_for_reading(items)
      self.assertEqual( b'apple.txt\n', tmp_archive.extract_member_to_string('foo/apple.txt') )
      self.assertEqual( b'{}\n', tmp_archive.extract_member_to_string('metadata/db.json') )
  
    def test_extract_member_to_file(self):
      items = temp_archive.make_temp_item_list([
        ( self.native_filename('foo/apple.txt'), 'apple.txt\n' ),
        ( self.native_filename('foo/durian.txt'), 'durian.txt\n' ),
        ( self.native_filename('foo/kiwi.txt'), 'kiwi.txt\n' ),
        ( self.native_filename('metadata/db.json'), '{}\n' ),
      ])
      tmp_archive = self.make_temp_archive_for_reading(items)
      tmp_file = self.make_temp_file(non_existent = True)
      tmp_archive.extract_member_to_file('foo/apple.txt', tmp_file)
      self.assertEqual( b'apple.txt\n', file_util.read(tmp_file) )
      
    def _test_extract_with_members(self, items, members,
                                   base_dir = None,
                                   strip_common_ancestor = False,
                                   strip_head = None):
      tmp_archive = self.make_temp_archive_for_reading(items)
      tmp_dir = self.make_temp_dir()
      tmp_archive.extract(tmp_dir,
                          base_dir = base_dir,
                          strip_common_ancestor = strip_common_ancestor,
                          strip_head = strip_head,
                          include = members)
      actual_files = file_find.find(tmp_dir, relative = True)
      file_util.remove(tmp_dir)
      return actual_files
  
    def test_extract_members(self):
      items = temp_archive.make_temp_item_list([
        ( self.native_filename('foo/apple.txt'), 'apple.txt\n' ),
        ( self.native_filename('foo/durian.txt'), 'durian.txt\n' ),
        ( self.native_filename('foo/kiwi.txt'), 'kiwi.txt\n' ),
        ( self.native_filename('metadata/db.json'), '{}\n' ),
      ])
      members = [
        'foo/apple.txt',
        'foo/durian.txt',
      ]
      actual_files = self._test_extract_with_members(items, members)
      expected_files = [ self.native_filename(m) for m in members ]
      self.assertEqual( expected_files, actual_files )
  
    def test_common_base(self):
      items = temp_archive.make_temp_item_list([
        ( self.native_filename('base-1.2.3/foo.txt'), 'foo.txt\n' ),
        ( self.native_filename('base-1.2.3/bar.txt'), 'bar.txt\n' ),
        ( self.native_filename('base-1.2.3/baz.txt'), 'baz.txt\n' ),
      ])
      tmp_archive = self.make_temp_archive_for_reading(items)
      self.assertEqual( 'base-1.2.3', self.make_temp_archive_for_reading(items).common_base() )
  
    def test_common_base_none(self):
      items = temp_archive.make_temp_item_list([
        ( self.native_filename('base-1.2.3/foo.txt'), 'foo.txt\n' ),
        ( self.native_filename('base-1.2.4/bar.txt'), 'bar.txt\n' ),
        ( self.native_filename('base-1.2.4/baz.txt'), 'bar.txt\n' ),
      ])
      self.assertEqual( None, self.make_temp_archive_for_reading(items).common_base() )
  
      items = temp_archive.make_temp_item_list([
        ( self.native_filename('bar.txt'), 'bar.txt\n' ),
        ( self.native_filename('baz.txt'), 'baz.txt\n' ),
      ])
      self.assertEqual( None, self.make_temp_archive_for_reading(items).common_base() )
  
      items = temp_archive.make_temp_item_list([
        ( self.native_filename('base/foo.txt'), 'foo.txt\n' ),
        ( self.native_filename('bar.txt'), 'bar.txt\n' ),
      ])
      self.assertEqual( None, self.make_temp_archive_for_reading(items).common_base() )
  
    def _compare_dirs(self, expected_dir, actual_dir, transform = None):
      # FIXME: How to pop this state ?
      self.maxDiff = None
  
      expected_files = file_find.find(expected_dir, relative = True)
      actual_files = file_find.find(actual_dir, relative = True)
  
      if transform:
        actual_files = [ transform(f) for f in actual_files ]
  
      self.assertEqual( expected_files, actual_files )
  
    def test_create_basic(self):
      self.maxDiff = None
  
      items = temp_archive.make_temp_item_list([
        ( self.native_filename('base-1.2.3/foo.txt'), 'foo.txt\n' ),
        ( self.native_filename('base-1.2.3/bar.txt'), 'bar.txt\n' ),
      ])
      
      tmp_dir = temp_archive.write_temp_items(items)
  
      archive = self.make_temp_archive_for_writing()
      archive.create(tmp_dir)
  
      self.assertTrue( path.isfile(archive.filename) )
  
      tmp_extract_dir = self.make_temp_dir()
      archive.extract_all(tmp_extract_dir)
  
      self._compare_dirs(tmp_dir, tmp_extract_dir)
  
      file_util.remove([ tmp_dir, tmp_extract_dir])
  
    def test_create_base_dir(self):
      self.maxDiff = None
  
      items = temp_archive.make_temp_item_list([
        ( self.native_filename('base-1.2.3/foo.txt'), 'foo.txt\n' ),
        ( self.native_filename('base-1.2.3/bar.txt'), 'bar.txt\n' ),
      ])
      
      tmp_dir = temp_archive.write_temp_items(items)
  
      base_dir = 'foo-666'
  
      archive = self.make_temp_archive_for_writing()
      archive.create(tmp_dir, base_dir = base_dir)
  
      self.assertTrue( path.isfile(archive.filename) )
  
      tmp_extract_dir = self.make_temp_dir()
      archive.extract_all(tmp_extract_dir)
  
      def _remove_base_dir(f):
        return file_util.remove_head(f, base_dir)
  
      self._compare_dirs(tmp_dir, tmp_extract_dir, transform = _remove_base_dir)
  
      file_util.remove([ tmp_dir, tmp_extract_dir])
  
    def test_create_with_include(self):
      self.maxDiff = None
      items = temp_archive.make_temp_item_list([
        ( self.native_filename('foo.txt'), 'foo.txt\n' ),
        ( self.native_filename('bar.txt'), 'bar.txt\n' ),
        ( self.native_filename('baz.png'), 'baz.png\n' ),
        ( self.native_filename('baz2.png'), 'baz2.png\n' ),
        ( self.native_filename('apple.pdf'), 'apple.pdf\n' ),
        ( self.native_filename('kiwi.pdf'), 'kiwi.pdf\n' ),
        ( self.native_filename('durian.pdf'), 'durian.pdf\n' ),
      ])
      include = [ '*.txt' ]
      exclude = None
      expected_files = [
        self.native_filename('bar.txt'),
        self.native_filename('foo.txt'),
      ]
      actual_files = self._test_create_with_include_exclude(items, include, exclude)
      self.assertEqual( expected_files, actual_files )
  
    def test_create_with_multiple_include(self):
      self.maxDiff = None
      items = temp_archive.make_temp_item_list([
        ( self.native_filename('foo.txt'), 'foo.txt\n' ),
        ( self.native_filename('bar.txt'), 'bar.txt\n' ),
        ( self.native_filename('baz.png'), 'baz.png\n' ),
        ( self.native_filename('baz2.png'), 'baz2.png\n' ),
        ( self.native_filename('apple.pdf'), 'apple.pdf\n' ),
        ( self.native_filename('kiwi.pdf'), 'kiwi.pdf\n' ),
        ( self.native_filename('durian.pdf'), 'durian.pdf\n' ),
      ])
      include = [ '*.txt', '*.png' ]
      exclude = None
      expected_files = [
        self.native_filename('bar.txt'),
        self.native_filename('baz.png'),
        self.native_filename('baz2.png'),
        self.native_filename('foo.txt'),
      ]
      actual_files = self._test_create_with_include_exclude(items, include, exclude)
      self.assertEqual( expected_files, actual_files )
  
    def test_create_with_exclude(self):
      self.maxDiff = None
      items = temp_archive.make_temp_item_list([
        ( self.native_filename('foo.txt'), 'foo.txt\n' ),
        ( self.native_filename('bar.txt'), 'bar.txt\n' ),
        ( self.native_filename('baz.png'), 'baz.png\n' ),
        ( self.native_filename('baz2.png'), 'baz2.png\n' ),
        ( self.native_filename('apple.pdf'), 'apple.pdf\n' ),
        ( self.native_filename('kiwi.pdf'), 'kiwi.pdf\n' ),
        ( self.native_filename('durian.pdf'), 'durian.pdf\n' ),
      ])
      include = None
      exclude = [ '*.txt' ]
      expected_files = [
        self.native_filename('apple.pdf'),
        self.native_filename('baz.png'),
        self.native_filename('baz2.png'),
        self.native_filename('durian.pdf'),
        self.native_filename('kiwi.pdf'),
      ]
      actual_files = self._test_create_with_include_exclude(items, include, exclude)
      self.assertEqual( expected_files, actual_files )
  
    def test_create_with_multiple_exclude(self):
      self.maxDiff = None
      items = temp_archive.make_temp_item_list([
        ( self.native_filename('foo.txt'), 'foo.txt\n' ),
        ( self.native_filename('bar.txt'), 'bar.txt\n' ),
        ( self.native_filename('baz.png'), 'baz.png\n' ),
        ( self.native_filename('baz2.png'), 'baz2.png\n' ),
        ( self.native_filename('apple.pdf'), 'apple.pdf\n' ),
        ( self.native_filename('kiwi.pdf'), 'kiwi.pdf\n' ),
        ( self.native_filename('durian.pdf'), 'durian.pdf\n' ),
      ])
      include = None
      exclude = [ '*.txt', '*.png' ]
      expected_files = [
        self.native_filename('apple.pdf'),
        self.native_filename('durian.pdf'),
        self.native_filename('kiwi.pdf'),
      ]
      actual_files = self._test_create_with_include_exclude(items, include, exclude)
      self.assertEqual( expected_files, actual_files )
  
    def test_create_with_include_and_exclude(self):
      self.maxDiff = None
      items = temp_archive.make_temp_item_list([
        ( self.native_filename('base-1.2.3/foo.txt'), 'foo.txt\n' ),
        ( self.native_filename('base-1.2.3/bar.txt'), 'bar.txt\n' ),
        ( self.native_filename('base-1.2.3/baz.png'), 'baz.png\n' ),
        ( self.native_filename('base-1.2.3/baz2.png'), 'baz2.png\n' ),
        ( self.native_filename('base-1.2.3/apple.pdf'), 'apple.pdf\n' ),
        ( self.native_filename('base-1.2.3/kiwi.pdf'), 'kiwi.pdf\n' ),
        ( self.native_filename('base-1.2.3/durian.pdf'), 'durian.pdf\n' ),
      ])
      include = [ '*.pdf' ]
      exclude = [ '*kiwi.pdf' ]
      expected_files = [
        self.native_filename('base-1.2.3/apple.pdf'),
        self.native_filename('base-1.2.3/durian.pdf'),
      ]
      actual_files = self._test_create_with_include_exclude(items, include, exclude)
      self.assertEqual( expected_files, actual_files )
  
    def _test_create_with_include_exclude(self, items, include, exclude):
      tmp_dir = temp_archive.write_temp_items(items)
      archive = self.make_temp_archive_for_writing()
      archive.create(tmp_dir, include = include, exclude = exclude)
      self.assertTrue( path.isfile(archive.filename) )
      tmp_extract_dir = self.make_temp_dir()
      archive.extract_all(tmp_extract_dir)
      actual_files = file_find.find(tmp_extract_dir, relative = True)
      file_util.remove([ tmp_dir, tmp_extract_dir])
      return actual_files
  
    def xtest_checksum(self):
      items = temp_archive.make_temp_item_list([
        ( self.native_filename('foo.txt'), 'foo.txt\n' ),
        ( self.native_filename('bar.txt'), 'bar.txt\n' ),
        ( self.native_filename('baz.png'), 'baz.png\n' ),
        ( self.native_filename('baz2.png'), 'baz2.png\n' ),
        ( self.native_filename('apple.pdf'), 'apple.pdf\n' ),
        ( self.native_filename('kiwi.pdf'), 'kiwi.pdf\n' ),
        ( self.native_filename('durian.pdf'), 'durian.pdf\n' ),
      ])
      tmp_dir = temp_archive.write_temp_items(items)
      archive1 = self.make_temp_archive_for_writing()
      archive1.create(tmp_dir)
      checksum1 = file_util.checksum('sha256', archive1.filename)
      
      archive2 = self.make_temp_archive_for_writing()
      archive2.create(tmp_dir)
      checksum2 = file_util.checksum('sha256', archive2.filename)
  
      self.assertEqual( checksum1, checksum2 )
  
    @classmethod
    def native_filename(clazz, s, pathsep = ':', sep = '/'):
      result = s.replace(pathsep, os.pathsep)
      result = result.replace(sep, os.sep)
      return result
  
    @classmethod
    def p(clazz, s, pathsep = ':', sep = '/'):
      return clazz.native_filename(s, pathsep = pathsep, sep = sep)
    
  return _archive_test_case

#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from abc import abstractmethod

from bes.fs import file_find, file_util, temp_file
from bes.match import matcher_multiple_filename, matcher_always_false, matcher_always_true
from bes.archive.temp_archive import temp_archive
from bes.testing.unit_test import unit_test

class common_archive_tests(object):
  'Superclass for archive unit tests for which logic is shared regardless of the archive type.'

  DEBUG = unit_test.DEBUG

  @abstractmethod
  def _make_archive(self, filename):
    pass

  def make_archive(self, filename):
    archive = self._make_archive(filename)
    if self.DEBUG:
      print("archive: ", archive.filename)
    return archive
  
  def make_temp_archive_for_reading(self, items, archive_type = None):
    archive_type = archive_type or self.default_archive_type
    assert archive_type
    tmp_archive = temp_archive.make_temp_archive(items, archive_type, delete = not self.DEBUG)
    return self.make_archive(tmp_archive.filename)

  def make_temp_archive_for_writing(self):
    tmp_archive = temp_file.make_temp_file(suffix = '.' + self.default_archive_type, delete = False)
    return self.make_archive(tmp_archive)

  def test_members(self):
    assert self.default_archive_type
    tmp_tar = temp_archive.make_temp_archive([ temp_archive.item('foo.txt', content = 'foo.txt\n') ], self.default_archive_type, delete = not self.DEBUG)
    self.assertEqual( [ 'foo.txt' ], self.make_archive(tmp_tar.filename).members )

  def test_has_member(self):
    assert self.default_archive_type

    items = temp_archive.make_temp_item_list([
      ( 'foo/apple.txt', 'apple.txt\n' ),
      ( 'foo/durian.txt', 'durian.txt\n' ),
      ( 'foo/kiwi.txt', 'kiwi.txt\n' ),
      ( 'metadata/db.json', '{}\n' ),
    ])
    tmp_archive = self.make_temp_archive_for_reading(items)
    self.assertTrue( self.make_archive(tmp_archive.filename).has_member('foo/apple.txt') )
    self.assertFalse( self.make_archive(tmp_archive.filename).has_member('nothere.txt') )

  def test_extract_all(self):
    assert self.default_archive_type
    items = temp_archive.make_temp_item_list([
      ( 'foo.txt', 'foo.txt\n' ),
    ])
    tmp_archive = self.make_temp_archive_for_reading(items)
    tmp_dir = temp_file.make_temp_dir()
    tmp_archive.extract_all(tmp_dir)
    self.assertTrue( path.isfile(path.join(tmp_dir, 'foo.txt')) )

  def test_extract_all_with_base_dir(self):
    assert self.default_archive_type
    items = temp_archive.make_temp_item_list([
      ( 'foo.txt', 'foo.txt\n' ),
    ])
    tmp_archive = self.make_temp_archive_for_reading(items)
    tmp_dir = temp_file.make_temp_dir()
    base_dir = 'base-1.2.3'
    tmp_archive.extract_all(tmp_dir, base_dir = base_dir)
    self.assertTrue( path.isfile(path.join(tmp_dir, base_dir, 'foo.txt')) )

  def test_extract_all_with_strip_common_ancestor(self):
    assert self.default_archive_type
    base_dir_to_strip = 'base-1.2.3'

    items = temp_archive.make_temp_item_list([
      ( 'foo.txt', 'foo.txt\n' ),
    ])
    items = temp_archive.add_base_dir(items, base_dir_to_strip)
    tmp_archive = self.make_temp_archive_for_reading(items)
    tmp_dir = temp_file.make_temp_dir()
    tmp_archive.extract_all(tmp_dir, strip_common_ancestor = True)
    self.assertTrue( path.isfile(path.join(tmp_dir, 'foo.txt')) )

  def test_extract_all_with_base_dir_and_strip_common_ancestor(self):
    assert self.default_archive_type
    base_dir_to_strip = 'base-1.2.3'
    items = temp_archive.make_temp_item_list([
      ( 'foo.txt', 'foo.txt\n' ),
    ])
    items = temp_archive.add_base_dir(items, base_dir_to_strip)
    base_dir_to_add = 'added-6.6.6'
    tmp_archive = self.make_temp_archive_for_reading(items)
    tmp_dir = temp_file.make_temp_dir()
    tmp_archive.extract_all(tmp_dir, base_dir = base_dir_to_add, strip_common_ancestor = True)
    self.assertTrue( path.isfile(path.join(tmp_dir, base_dir_to_add, 'foo.txt')) )

  def test_extract_all_with_strip_head(self):
    assert self.default_archive_type

    items = temp_archive.make_temp_item_list([
      ( 'foo/apple.txt', 'apple.txt\n' ),
      ( 'foo/durian.txt', 'durian.txt\n' ),
      ( 'foo/kiwi.txt', 'kiwi.txt\n' ),
      ( 'metadata/db.json', '{}\n' ),
    ])
    tmp_archive = self.make_temp_archive_for_reading(items)
    tmp_dir = temp_file.make_temp_dir()
    tmp_archive.extract_all(tmp_dir, strip_head = 'foo')

    actual_files = file_find.find(tmp_dir, relative = True)

    expected_files = [
      'apple.txt',
      'durian.txt',
      'kiwi.txt',
      'metadata/db.json',
    ]

    self.assertEqual( expected_files, actual_files )

  def test_extract_all_with_strip_common_ancestor_and_strip_head(self):
    assert self.default_archive_type

    items = temp_archive.make_temp_item_list([
      ( 'base-1.2.3/foo/apple.txt', 'apple.txt\n' ),
      ( 'base-1.2.3/foo/durian.txt', 'durian.txt\n' ),
      ( 'base-1.2.3/foo/kiwi.txt', 'kiwi.txt\n' ),
      ( 'base-1.2.3/metadata/db.json', '{}\n' ),
    ])
    tmp_archive = self.make_temp_archive_for_reading(items)
    tmp_dir = temp_file.make_temp_dir()
    tmp_archive.extract_all(tmp_dir, strip_common_ancestor = True, strip_head = 'foo')

    actual_files = file_find.find(tmp_dir, relative = True)

    expected_files = [
      'apple.txt',
      'durian.txt',
      'kiwi.txt',
      'metadata/db.json',
    ]

    self.assertEqual( expected_files, actual_files )

  def test_extract_all_overlap(self):
    assert self.default_archive_type

    items1 = temp_archive.make_temp_item_list([
      ( 'base-1.2.3/foo.txt', 'foo.txt\n' ),
      ( 'base-1.2.3/bar.txt', 'bar.txt\n' ),
    ])

    items2 = temp_archive.make_temp_item_list([
      ( 'base-1.2.3/orange.txt', 'orange.txt\n' ),
      ( 'base-1.2.3/kiwi.txt', 'kiwi.txt\n' ),
    ])

    tmp_archive1 = self.make_temp_archive_for_reading(items1)
    tmp_archive2 = self.make_temp_archive_for_reading(items2)

    tmp_dir = temp_file.make_temp_dir()
    tmp_archive1.extract_all(tmp_dir)
    tmp_archive2.extract_all(tmp_dir)

    actual_files = file_find.find(tmp_dir, relative = True)

    expected_files = [
      'base-1.2.3/bar.txt',
      'base-1.2.3/foo.txt',
      'base-1.2.3/kiwi.txt',
      'base-1.2.3/orange.txt',
    ]

    self.assertEqual( expected_files, actual_files )

  def test_extract_all_overlap_with_base_dir(self):
    assert self.default_archive_type

    items1 = temp_archive.make_temp_item_list([
      ( 'base-1.2.3/foo.txt', 'foo.txt\n' ),
      ( 'base-1.2.3/bar.txt', 'bar.txt\n' ),
    ])

    items2 = temp_archive.make_temp_item_list([
      ( 'base-1.2.3/orange.txt', 'orange.txt\n' ),
      ( 'base-1.2.3/kiwi.txt', 'kiwi.txt\n' ),
    ])

    tmp_archive1 = self.make_temp_archive_for_reading(items1)
    tmp_archive2 = self.make_temp_archive_for_reading(items2)

    tmp_dir = temp_file.make_temp_dir()
    base_dir = 'foo-6.6.6'
    tmp_archive1.extract_all(tmp_dir, base_dir = base_dir)
    tmp_archive2.extract_all(tmp_dir, base_dir = base_dir)

    actual_files = file_find.find(tmp_dir, relative = True)

    expected_files = [
      'foo-6.6.6/base-1.2.3/bar.txt',
      'foo-6.6.6/base-1.2.3/foo.txt',
      'foo-6.6.6/base-1.2.3/kiwi.txt',
      'foo-6.6.6/base-1.2.3/orange.txt',
    ]

    self.assertEqual( expected_files, actual_files )

  def test_extract_all_overlap_with_base_dir_and_strip_common_ancestor(self):
    assert self.default_archive_type

    items1 = temp_archive.make_temp_item_list([
      ( 'base-1.2.3/foo.txt', 'foo.txt\n' ),
      ( 'base-1.2.3/subdir/bar.txt', 'bar.txt\n' ),
    ])

    items2 = temp_archive.make_temp_item_list([
      ( 'notbase-1.2.3/orange.txt', 'orange.txt\n' ),
      ( 'notbase-1.2.3/subdir/kiwi.txt', 'kiwi.txt\n' ),
    ])

    tmp_archive1 = self.make_temp_archive_for_reading(items1)
    tmp_archive2 = self.make_temp_archive_for_reading(items2)

    tmp_dir = temp_file.make_temp_dir()
    base_dir = 'foo-6.6.6'
    tmp_archive1.extract_all(tmp_dir, base_dir = base_dir, strip_common_ancestor = True)
    tmp_archive2.extract_all(tmp_dir, base_dir = base_dir, strip_common_ancestor = True)

    actual_files = file_find.find(tmp_dir, relative = True)
    expected_files = [
      'foo-6.6.6/foo.txt',
      'foo-6.6.6/orange.txt',
      'foo-6.6.6/subdir/bar.txt',
      'foo-6.6.6/subdir/kiwi.txt',
    ]
    self.assertEqual( expected_files, actual_files )

  def test_extract_with_include(self):
    assert self.default_archive_type
    items = temp_archive.make_temp_item_list([
      ( 'foo/apple.txt', 'apple.txt\n' ),
      ( 'foo/durian.txt', 'durian.txt\n' ),
      ( 'foo/kiwi.txt', 'kiwi.txt\n' ),
      ( 'metadata/db.json', '{}\n' ),
    ])
    include = [ '*.txt' ]
    exclude = None
    actual_files = self._test_extract_with_include_exclude(items, include, exclude)
    expected_files = [
      'foo/apple.txt',
      'foo/durian.txt',
      'foo/kiwi.txt',
    ]
    self.assertEqual( expected_files, actual_files )

  def test_extract_with_exclude(self):
    assert self.default_archive_type
    items = temp_archive.make_temp_item_list([
      ( 'foo/apple.txt', 'apple.txt\n' ),
      ( 'foo/durian.txt', 'durian.txt\n' ),
      ( 'foo/kiwi.txt', 'kiwi.txt\n' ),
      ( 'metadata/db.json', '{}\n' ),
    ])
    include = None
    exclude = [ '*.txt' ]
    actual_files = self._test_extract_with_include_exclude(items, include, exclude)
    expected_files = [
      'metadata/db.json',
    ]
    self.assertEqual( expected_files, actual_files )

  def test_extract_with_include_and_exclude(self):
    assert self.default_archive_type
    items = temp_archive.make_temp_item_list([
      ( 'foo/apple.txt', 'apple.txt\n' ),
      ( 'foo/durian.txt', 'durian.txt\n' ),
      ( 'foo/kiwi.txt', 'kiwi.txt\n' ),
      ( 'metadata/db.json', '{}\n' ),
    ])
    include = [ '*.txt' ]
    exclude = [ '*durian*' ]
    actual_files = self._test_extract_with_include_exclude(items, include, exclude)

    expected_files = [
      'foo/apple.txt',
      'foo/kiwi.txt',
    ]
    self.assertEqual( expected_files, actual_files )

  def _test_extract_with_include_exclude(self, items, include, exclude):
    tmp_archive = self.make_temp_archive_for_reading(items)
    tmp_dir = temp_file.make_temp_dir()
    tmp_archive.extract(tmp_dir, include = include, exclude = exclude)
    actual_files = file_find.find(tmp_dir, relative = True)
    file_util.remove(tmp_dir)
    return actual_files

  def test_extract_member_to_string(self):
    assert self.default_archive_type
    items = temp_archive.make_temp_item_list([
      ( 'foo/apple.txt', 'apple.txt\n' ),
      ( 'foo/durian.txt', 'durian.txt\n' ),
      ( 'foo/kiwi.txt', 'kiwi.txt\n' ),
      ( 'metadata/db.json', '{}\n' ),
    ])
    tmp_archive = self.make_temp_archive_for_reading(items)
    self.assertEqual( b'apple.txt\n', tmp_archive.extract_member_to_string('foo/apple.txt') )
    self.assertEqual( b'{}\n', tmp_archive.extract_member_to_string('metadata/db.json') )

  def test_extract_member_to_file(self):
    assert self.default_archive_type
    items = temp_archive.make_temp_item_list([
      ( 'foo/apple.txt', 'apple.txt\n' ),
      ( 'foo/durian.txt', 'durian.txt\n' ),
      ( 'foo/kiwi.txt', 'kiwi.txt\n' ),
      ( 'metadata/db.json', '{}\n' ),
    ])
    tmp_archive = self.make_temp_archive_for_reading(items)
    tmp_file = temp_file.make_temp_file()
    tmp_archive.extract_member_to_file('foo/apple.txt', tmp_file)
    self.assertEqual( b'apple.txt\n', file_util.read(tmp_file) )
    
  def _test_extract_with_members(self, items, members,
                                 base_dir = None,
                                 strip_common_ancestor = False,
                                 strip_head = None):
    tmp_archive = self.make_temp_archive_for_reading(items)
    tmp_dir = temp_file.make_temp_dir()
    tmp_archive.extract(tmp_dir,
                        base_dir = base_dir,
                        strip_common_ancestor = strip_common_ancestor,
                        strip_head = strip_head,
                        include = members)
    actual_files = file_find.find(tmp_dir, relative = True)
    file_util.remove(tmp_dir)
    return actual_files

  def test_extract_members(self):
    assert self.default_archive_type
    items = temp_archive.make_temp_item_list([
      ( 'foo/apple.txt', 'apple.txt\n' ),
      ( 'foo/durian.txt', 'durian.txt\n' ),
      ( 'foo/kiwi.txt', 'kiwi.txt\n' ),
      ( 'metadata/db.json', '{}\n' ),
    ])
    members = [
      'foo/apple.txt',
      'foo/durian.txt',
    ]
    actual_files = self._test_extract_with_members(items, members)
    expected_files = members
    self.assertEqual( expected_files, actual_files )

  def test_common_base(self):
    items = temp_archive.make_temp_item_list([
      ( 'base-1.2.3/foo.txt', 'foo.txt\n' ),
      ( 'base-1.2.3/bar.txt', 'bar.txt\n' ),
      ( 'base-1.2.3/baz.txt', 'baz.txt\n' ),
    ])
    tmp_archive = self.make_temp_archive_for_reading(items)
    self.assertEqual( 'base-1.2.3', self.make_temp_archive_for_reading(items).common_base() )

  def test_common_base_none(self):
    items = temp_archive.make_temp_item_list([
      ( 'base-1.2.3/foo.txt', 'foo.txt\n' ),
      ( 'base-1.2.4/bar.txt', 'bar.txt\n' ),
      ( 'base-1.2.4/baz.txt', 'bar.txt\n' ),
    ])
    self.assertEqual( None, self.make_temp_archive_for_reading(items).common_base() )

    items = temp_archive.make_temp_item_list([
      ( 'bar.txt', 'bar.txt\n' ),
      ( 'baz.txt', 'baz.txt\n' ),
    ])
    self.assertEqual( None, self.make_temp_archive_for_reading(items).common_base() )

    items = temp_archive.make_temp_item_list([
      ( 'base/foo.txt', 'foo.txt\n' ),
      ( 'bar.txt', 'bar.txt\n' ),
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
      ( 'base-1.2.3/foo.txt', 'foo.txt\n' ),
      ( 'base-1.2.3/bar.txt', 'bar.txt\n' ),
    ])
    
    tmp_dir = temp_archive.write_temp_items(items)

    archive = self.make_temp_archive_for_writing()
    archive.create(tmp_dir)

    self.assertTrue( path.isfile(archive.filename) )

    tmp_extract_dir = temp_file.make_temp_dir()
    archive.extract_all(tmp_extract_dir)

    self._compare_dirs(tmp_dir, tmp_extract_dir)

    file_util.remove([ tmp_dir, tmp_extract_dir])

  def test_create_base_dir(self):
    self.maxDiff = None

    items = temp_archive.make_temp_item_list([
      ( 'base-1.2.3/foo.txt', 'foo.txt\n' ),
      ( 'base-1.2.3/bar.txt', 'bar.txt\n' ),
    ])
    
    tmp_dir = temp_archive.write_temp_items(items)

    base_dir = 'foo-666'

    archive = self.make_temp_archive_for_writing()
    archive.create(tmp_dir, base_dir = base_dir)

    self.assertTrue( path.isfile(archive.filename) )

    tmp_extract_dir = temp_file.make_temp_dir()
    archive.extract_all(tmp_extract_dir)

    def _remove_base_dir(f):
      return file_util.remove_head(f, base_dir)

    self._compare_dirs(tmp_dir, tmp_extract_dir, transform = _remove_base_dir)

    file_util.remove([ tmp_dir, tmp_extract_dir])

  def test_create_with_include(self):
    self.maxDiff = None
    items = temp_archive.make_temp_item_list([
      ( 'foo.txt', 'foo.txt\n' ),
      ( 'bar.txt', 'bar.txt\n' ),
      ( 'baz.png', 'baz.png\n' ),
      ( 'baz2.png', 'baz2.png\n' ),
      ( 'apple.pdf', 'apple.pdf\n' ),
      ( 'kiwi.pdf', 'kiwi.pdf\n' ),
      ( 'durian.pdf', 'durian.pdf\n' ),
    ])
    include = [ '*.txt' ]
    exclude = None
    expected_files = [
      'bar.txt',
      'foo.txt',
    ]
    actual_files = self._test_create_with_include_exclude(items, include, exclude)
    self.assertEqual( expected_files, actual_files )

  def test_create_with_multiple_include(self):
    self.maxDiff = None
    items = temp_archive.make_temp_item_list([
      ( 'foo.txt', 'foo.txt\n' ),
      ( 'bar.txt', 'bar.txt\n' ),
      ( 'baz.png', 'baz.png\n' ),
      ( 'baz2.png', 'baz2.png\n' ),
      ( 'apple.pdf', 'apple.pdf\n' ),
      ( 'kiwi.pdf', 'kiwi.pdf\n' ),
      ( 'durian.pdf', 'durian.pdf\n' ),
    ])
    include = [ '*.txt', '*.png' ]
    exclude = None
    expected_files = [
      'bar.txt',
      'baz.png',
      'baz2.png',
      'foo.txt',
    ]
    actual_files = self._test_create_with_include_exclude(items, include, exclude)
    self.assertEqual( expected_files, actual_files )

  def test_create_with_exclude(self):
    self.maxDiff = None
    items = temp_archive.make_temp_item_list([
      ( 'foo.txt', 'foo.txt\n' ),
      ( 'bar.txt', 'bar.txt\n' ),
      ( 'baz.png', 'baz.png\n' ),
      ( 'baz2.png', 'baz2.png\n' ),
      ( 'apple.pdf', 'apple.pdf\n' ),
      ( 'kiwi.pdf', 'kiwi.pdf\n' ),
      ( 'durian.pdf', 'durian.pdf\n' ),
    ])
    include = None
    exclude = [ '*.txt' ]
    expected_files = [
      'apple.pdf',
      'baz.png',
      'baz2.png',
      'durian.pdf',
      'kiwi.pdf',
    ]
    actual_files = self._test_create_with_include_exclude(items, include, exclude)
    self.assertEqual( expected_files, actual_files )

  def test_create_with_multiple_exclude(self):
    self.maxDiff = None
    items = temp_archive.make_temp_item_list([
      ( 'foo.txt', 'foo.txt\n' ),
      ( 'bar.txt', 'bar.txt\n' ),
      ( 'baz.png', 'baz.png\n' ),
      ( 'baz2.png', 'baz2.png\n' ),
      ( 'apple.pdf', 'apple.pdf\n' ),
      ( 'kiwi.pdf', 'kiwi.pdf\n' ),
      ( 'durian.pdf', 'durian.pdf\n' ),
    ])
    include = None
    exclude = [ '*.txt', '*.png' ]
    expected_files = [
      'apple.pdf',
      'durian.pdf',
      'kiwi.pdf',
    ]
    actual_files = self._test_create_with_include_exclude(items, include, exclude)
    self.assertEqual( expected_files, actual_files )

  def test_create_with_include_and_exclude(self):
    self.maxDiff = None
    items = temp_archive.make_temp_item_list([
      ( 'base-1.2.3/foo.txt', 'foo.txt\n' ),
      ( 'base-1.2.3/bar.txt', 'bar.txt\n' ),
      ( 'base-1.2.3/baz.png', 'baz.png\n' ),
      ( 'base-1.2.3/baz2.png', 'baz2.png\n' ),
      ( 'base-1.2.3/apple.pdf', 'apple.pdf\n' ),
      ( 'base-1.2.3/kiwi.pdf', 'kiwi.pdf\n' ),
      ( 'base-1.2.3/durian.pdf', 'durian.pdf\n' ),
    ])
    include = [ '*.pdf' ]
    exclude = [ '*kiwi.pdf' ]
    expected_files = [
      'base-1.2.3/apple.pdf',
      'base-1.2.3/durian.pdf',
    ]
    actual_files = self._test_create_with_include_exclude(items, include, exclude)
    self.assertEqual( expected_files, actual_files )

  def _test_create_with_include_exclude(self, items, include, exclude):
    tmp_dir = temp_archive.write_temp_items(items)
    archive = self.make_temp_archive_for_writing()
    archive.create(tmp_dir, include = include, exclude = exclude)
    self.assertTrue( path.isfile(archive.filename) )
    tmp_extract_dir = temp_file.make_temp_dir()
    archive.extract_all(tmp_extract_dir)
    actual_files = file_find.find(tmp_extract_dir, relative = True)
    file_util.remove([ tmp_dir, tmp_extract_dir])
    return actual_files

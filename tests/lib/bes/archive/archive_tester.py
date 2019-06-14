#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, os.path as path
from abc import abstractmethod

from bes.archive.temp_archive import temp_archive
from bes.common.check import check
from bes.fs.file_find import file_find
from bes.fs.file_util import file_util
from bes.match.matcher_always_false import matcher_always_false
from bes.match.matcher_always_true import matcher_always_true
from bes.match.matcher_filename import matcher_multiple_filename

class archive_tester(object):
  'Helper that implements the logic for a lot of archive tests.'
  def __init__(self, unit_test, archive_class, archive_type, debug):
    self._unit_test = unit_test
    self._archive_class = archive_class
    self._archive_type = archive_type
    self._debug = debug

  def make_archive(self, filename):
    check.check_string(filename)
    archive = self._archive_class(filename)
    if self._debug:
      print('archive: {}'.format(archive.filename))
    return archive
  
  def make_temp_archive_for_reading(self, items, archive_type = None):
    archive_type = archive_type or self._archive_type
    assert archive_type
    tmp_archive = temp_archive.make_temp_archive(items, archive_type, delete = not self._debug)
    return self.make_archive(tmp_archive)

  def make_temp_archive_for_writing(self):
    tmp_archive = self._unit_test.make_temp_file(suffix = '.' + self._archive_type)
    return self.make_archive(tmp_archive)

  def test_members(self):
    assert self._archive_type
    tmp_tar = temp_archive.make_temp_archive([ temp_archive.item('foo.txt', content = 'foo.txt\n') ], self._archive_type, delete = not self._debug)
    self._unit_test.assertEqual( [ 'foo.txt' ], self.make_archive(tmp_tar).members )

  def test_has_member(self):
    items = temp_archive.make_temp_item_list([
      ( self.xp_path('foo/apple.txt'), 'apple.txt\n' ),
      ( self.xp_path('foo/durian.txt'), 'durian.txt\n' ),
      ( self.xp_path('foo/kiwi.txt'), 'kiwi.txt\n' ),
      ( self.xp_path('metadata/db.json'), '{}\n' ),
    ])
    tmp_archive = self.make_temp_archive_for_reading(items)
    self._unit_test.assertTrue( self.make_archive(tmp_archive.filename).has_member('foo/apple.txt') )
    self._unit_test.assertFalse( self.make_archive(tmp_archive.filename).has_member('nothere.txt') )

  def test_extract_all(self):
    items = temp_archive.make_temp_item_list([
      ( self.xp_path('foo.txt'), 'foo.txt\n' ),
    ])
    tmp_archive = self.make_temp_archive_for_reading(items)
    tmp_dir = self._unit_test.make_temp_dir()
    tmp_archive.extract_all(tmp_dir)
    self._unit_test.assertTrue( path.isfile(path.join(tmp_dir, self.xp_path('foo.txt'))) )

  def test_extract_all_with_base_dir(self):
    items = temp_archive.make_temp_item_list([
      ( self.xp_path('foo.txt'), 'foo.txt\n' ),
    ])
    tmp_archive = self.make_temp_archive_for_reading(items)
    tmp_dir = self._unit_test.make_temp_dir()
    base_dir = self.xp_path('base-1.2.3')
    tmp_archive.extract_all(tmp_dir, base_dir = base_dir)
    self._unit_test.assertTrue( path.isfile(path.join(tmp_dir, base_dir, self.xp_path('foo.txt'))) )

  def test_extract_all_with_strip_common_ancestor(self):
    base_dir_to_strip = self.xp_path('base-1.2.3')
    items = temp_archive.make_temp_item_list([
      ( self.xp_path('foo.txt'), 'foo.txt\n' ),
    ])
    items = temp_archive.add_base_dir(items, base_dir_to_strip)
    tmp_archive = self.make_temp_archive_for_reading(items)
    tmp_dir = self._unit_test.make_temp_dir()
    tmp_archive.extract_all(tmp_dir, strip_common_ancestor = True)
    self._unit_test.assertTrue( path.isfile(path.join(tmp_dir, self.xp_path('foo.txt'))) )

  def test_extract_all_with_base_dir_and_strip_common_ancestor(self):
    base_dir_to_strip = self.xp_path('base-1.2.3')
    items = temp_archive.make_temp_item_list([
      ( self.xp_path('foo.txt'), 'foo.txt\n' ),
    ])
    items = temp_archive.add_base_dir(items, base_dir_to_strip)
    base_dir_to_add = self.xp_path('added-6.6.6')
    tmp_archive = self.make_temp_archive_for_reading(items)
    tmp_dir = self._unit_test.make_temp_dir()
    tmp_archive.extract_all(tmp_dir, base_dir = base_dir_to_add, strip_common_ancestor = True)
    self._unit_test.assertTrue( path.isfile(path.join(tmp_dir, base_dir_to_add, self.xp_path('foo.txt'))) )

  def test_extract_all_with_strip_head(self):

    items = temp_archive.make_temp_item_list([
      ( self.xp_path('foo/apple.txt'), 'apple.txt\n' ),
      ( self.xp_path('foo/durian.txt'), 'durian.txt\n' ),
      ( self.xp_path('foo/kiwi.txt'), 'kiwi.txt\n' ),
      ( self.xp_path('metadata/db.json'), '{}\n' ),
    ])
    tmp_archive = self.make_temp_archive_for_reading(items)
    tmp_dir = self._unit_test.make_temp_dir()
    tmp_archive.extract_all(tmp_dir, strip_head = self.xp_path('foo'))

    actual_files = file_find.find(tmp_dir, relative = True)

    expected_files = [
      self.xp_path('apple.txt'),
      self.xp_path('durian.txt'),
      self.xp_path('kiwi.txt'),
      self.xp_path('metadata/db.json'),
    ]

    self._unit_test.assertEqual( expected_files, actual_files )

  def test_extract_all_with_strip_common_ancestor_and_strip_head(self):

    items = temp_archive.make_temp_item_list([
      ( self.xp_path('base-1.2.3/foo/apple.txt'), 'apple.txt\n' ),
      ( self.xp_path('base-1.2.3/foo/durian.txt'), 'durian.txt\n' ),
      ( self.xp_path('base-1.2.3/foo/kiwi.txt'), 'kiwi.txt\n' ),
      ( self.xp_path('base-1.2.3/metadata/db.json'), '{}\n' ),
    ])
    tmp_archive = self.make_temp_archive_for_reading(items)
    tmp_dir = self._unit_test.make_temp_dir()
    tmp_archive.extract_all(tmp_dir, strip_common_ancestor = True, strip_head = self.xp_path('foo'))

    actual_files = file_find.find(tmp_dir, relative = True)

    expected_files = [
      self.xp_path('apple.txt'),
      self.xp_path('durian.txt'),
      self.xp_path('kiwi.txt'),
      self.xp_path('metadata/db.json'),
    ]

    self._unit_test.assertEqual( expected_files, actual_files )

  def test_extract_all_overlap(self):

    items1 = temp_archive.make_temp_item_list([
      ( self.xp_path('base-1.2.3/foo.txt'), 'foo.txt\n' ),
      ( self.xp_path('base-1.2.3/bar.txt'), 'bar.txt\n' ),
    ])

    items2 = temp_archive.make_temp_item_list([
      ( self.xp_path('base-1.2.3/orange.txt'), 'orange.txt\n' ),
      ( self.xp_path('base-1.2.3/kiwi.txt'), 'kiwi.txt\n' ),
    ])

    tmp_archive1 = self.make_temp_archive_for_reading(items1)
    tmp_archive2 = self.make_temp_archive_for_reading(items2)

    tmp_dir = self._unit_test.make_temp_dir()
    tmp_archive1.extract_all(tmp_dir)
    tmp_archive2.extract_all(tmp_dir)

    actual_files = file_find.find(tmp_dir, relative = True)

    expected_files = [
      self.xp_path('base-1.2.3/bar.txt'),
      self.xp_path('base-1.2.3/foo.txt'),
      self.xp_path('base-1.2.3/kiwi.txt'),
      self.xp_path('base-1.2.3/orange.txt'),
    ]

    self._unit_test.assertEqual( expected_files, actual_files )

  def test_extract_all_overlap_with_base_dir(self):

    items1 = temp_archive.make_temp_item_list([
      ( self.xp_path('base-1.2.3/foo.txt'), 'foo.txt\n' ),
      ( self.xp_path('base-1.2.3/bar.txt'), 'bar.txt\n' ),
    ])

    items2 = temp_archive.make_temp_item_list([
      ( self.xp_path('base-1.2.3/orange.txt'), 'orange.txt\n' ),
      ( self.xp_path('base-1.2.3/kiwi.txt'), 'kiwi.txt\n' ),
    ])

    tmp_archive1 = self.make_temp_archive_for_reading(items1)
    tmp_archive2 = self.make_temp_archive_for_reading(items2)

    tmp_dir = self._unit_test.make_temp_dir()
    base_dir = self.xp_path('foo-6.6.6')
    tmp_archive1.extract_all(tmp_dir, base_dir = base_dir)
    tmp_archive2.extract_all(tmp_dir, base_dir = base_dir)

    actual_files = file_find.find(tmp_dir, relative = True)

    expected_files = [
      self.xp_path('foo-6.6.6/base-1.2.3/bar.txt'),
      self.xp_path('foo-6.6.6/base-1.2.3/foo.txt'),
      self.xp_path('foo-6.6.6/base-1.2.3/kiwi.txt'),
      self.xp_path('foo-6.6.6/base-1.2.3/orange.txt'),
    ]

    self._unit_test.assertEqual( expected_files, actual_files )

  def test_extract_all_overlap_with_base_dir_and_strip_common_ancestor(self):

    items1 = temp_archive.make_temp_item_list([
      ( self.xp_path('base-1.2.3/foo.txt'), 'foo.txt\n' ),
      ( self.xp_path('base-1.2.3/subdir/bar.txt'), 'bar.txt\n' ),
    ])

    items2 = temp_archive.make_temp_item_list([
      ( self.xp_path('notbase-1.2.3/orange.txt'), 'orange.txt\n' ),
      ( self.xp_path('notbase-1.2.3/subdir/kiwi.txt'), 'kiwi.txt\n' ),
    ])

    tmp_archive1 = self.make_temp_archive_for_reading(items1)
    tmp_archive2 = self.make_temp_archive_for_reading(items2)

    tmp_dir = self._unit_test.make_temp_dir()
    base_dir = self.xp_path('foo-6.6.6')
    tmp_archive1.extract_all(tmp_dir, base_dir = base_dir, strip_common_ancestor = True)
    tmp_archive2.extract_all(tmp_dir, base_dir = base_dir, strip_common_ancestor = True)

    actual_files = file_find.find(tmp_dir, relative = True)
    expected_files = [
      self.xp_path('foo-6.6.6/foo.txt'),
      self.xp_path('foo-6.6.6/orange.txt'),
      self.xp_path('foo-6.6.6/subdir/bar.txt'),
      self.xp_path('foo-6.6.6/subdir/kiwi.txt'),
    ]
    self._unit_test.assertEqual( expected_files, actual_files )

  def test_extract_with_include(self):
    items = temp_archive.make_temp_item_list([
      ( self.xp_path('foo/apple.txt'), 'apple.txt\n' ),
      ( self.xp_path('foo/durian.txt'), 'durian.txt\n' ),
      ( self.xp_path('foo/kiwi.txt'), 'kiwi.txt\n' ),
      ( self.xp_path('metadata/db.json'), '{}\n' ),
    ])
    include = [ self.xp_path('*.txt') ]
    exclude = None
    actual_files = self._test_extract_with_include_exclude(items, include, exclude)
    expected_files = [
      self.xp_path('foo/apple.txt'),
      self.xp_path('foo/durian.txt'),
      self.xp_path('foo/kiwi.txt'),
    ]
    self._unit_test.assertEqual( expected_files, actual_files )

  def test_extract_with_exclude(self):
    items = temp_archive.make_temp_item_list([
      ( self.xp_path('foo/apple.txt'), 'apple.txt\n' ),
      ( self.xp_path('foo/durian.txt'), 'durian.txt\n' ),
      ( self.xp_path('foo/kiwi.txt'), 'kiwi.txt\n' ),
      ( self.xp_path('metadata/db.json'), '{}\n' ),
    ])
    include = None
    exclude = [ self.xp_path('*.txt') ]
    actual_files = self._test_extract_with_include_exclude(items, include, exclude)
    expected_files = [
      self.xp_path('metadata/db.json'),
    ]
    self._unit_test.assertEqual( expected_files, actual_files )

  def test_extract_with_include_and_exclude(self):
    items = temp_archive.make_temp_item_list([
      ( self.xp_path('foo/apple.txt'), 'apple.txt\n' ),
      ( self.xp_path('foo/durian.txt'), 'durian.txt\n' ),
      ( self.xp_path('foo/kiwi.txt'), 'kiwi.txt\n' ),
      ( self.xp_path('metadata/db.json'), '{}\n' ),
    ])
    include = [ '*.txt' ]
    exclude = [ '*durian*' ]
    actual_files = self._test_extract_with_include_exclude(items, include, exclude)

    expected_files = [
      self.xp_path('foo/apple.txt'),
      self.xp_path('foo/kiwi.txt'),
    ]
    self._unit_test.assertEqual( expected_files, actual_files )

  def _test_extract_with_include_exclude(self, items, include, exclude):
    tmp_archive = self.make_temp_archive_for_reading(items)
    tmp_dir = self._unit_test.make_temp_dir()
    tmp_archive.extract(tmp_dir, include = include, exclude = exclude)
    actual_files = file_find.find(tmp_dir, relative = True)
    file_util.remove(tmp_dir)
    return actual_files

  def test_extract_member_to_string(self):
    items = temp_archive.make_temp_item_list([
      ( self.xp_path('foo/apple.txt'), 'apple.txt\n' ),
      ( self.xp_path('foo/durian.txt'), 'durian.txt\n' ),
      ( self.xp_path('foo/kiwi.txt'), 'kiwi.txt\n' ),
      ( self.xp_path('metadata/db.json'), '{}\n' ),
    ])
    tmp_archive = self.make_temp_archive_for_reading(items)
    self._unit_test.assertEqual( b'apple.txt\n', tmp_archive.extract_member_to_string('foo/apple.txt') )
    self._unit_test.assertEqual( b'{}\n', tmp_archive.extract_member_to_string('metadata/db.json') )

  def test_extract_member_to_file(self):
    items = temp_archive.make_temp_item_list([
      ( self.xp_path('foo/apple.txt'), 'apple.txt\n' ),
      ( self.xp_path('foo/durian.txt'), 'durian.txt\n' ),
      ( self.xp_path('foo/kiwi.txt'), 'kiwi.txt\n' ),
      ( self.xp_path('metadata/db.json'), '{}\n' ),
    ])
    tmp_archive = self.make_temp_archive_for_reading(items)
    tmp_file = self._unit_test.make_temp_file()
    tmp_archive.extract_member_to_file('foo/apple.txt', tmp_file)
    self._unit_test.assertEqual( b'apple.txt\n', file_util.read(tmp_file) )
    
  def _test_extract_with_members(self, items, members,
                                 base_dir = None,
                                 strip_common_ancestor = False,
                                 strip_head = None):
    tmp_archive = self.make_temp_archive_for_reading(items)
    tmp_dir = self._unit_test.make_temp_dir()
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
      ( self.xp_path('foo/apple.txt'), 'apple.txt\n' ),
      ( self.xp_path('foo/durian.txt'), 'durian.txt\n' ),
      ( self.xp_path('foo/kiwi.txt'), 'kiwi.txt\n' ),
      ( self.xp_path('metadata/db.json'), '{}\n' ),
    ])
    members = [
      'foo/apple.txt',
      'foo/durian.txt',
    ]
    actual_files = self._test_extract_with_members(items, members)
    expected_files = [ self.xp_path(m) for m in members ]
    self._unit_test.assertEqual( expected_files, actual_files )

  def test_common_base(self):
    items = temp_archive.make_temp_item_list([
      ( self.xp_path('base-1.2.3/foo.txt'), 'foo.txt\n' ),
      ( self.xp_path('base-1.2.3/bar.txt'), 'bar.txt\n' ),
      ( self.xp_path('base-1.2.3/baz.txt'), 'baz.txt\n' ),
    ])
    tmp_archive = self.make_temp_archive_for_reading(items)
    self._unit_test.assertEqual( 'base-1.2.3', self.make_temp_archive_for_reading(items).common_base() )

  def test_common_base_none(self):
    items = temp_archive.make_temp_item_list([
      ( self.xp_path('base-1.2.3/foo.txt'), 'foo.txt\n' ),
      ( self.xp_path('base-1.2.4/bar.txt'), 'bar.txt\n' ),
      ( self.xp_path('base-1.2.4/baz.txt'), 'bar.txt\n' ),
    ])
    self._unit_test.assertEqual( None, self.make_temp_archive_for_reading(items).common_base() )

    items = temp_archive.make_temp_item_list([
      ( self.xp_path('bar.txt'), 'bar.txt\n' ),
      ( self.xp_path('baz.txt'), 'baz.txt\n' ),
    ])
    self._unit_test.assertEqual( None, self.make_temp_archive_for_reading(items).common_base() )

    items = temp_archive.make_temp_item_list([
      ( self.xp_path('base/foo.txt'), 'foo.txt\n' ),
      ( self.xp_path('bar.txt'), 'bar.txt\n' ),
    ])
    self._unit_test.assertEqual( None, self.make_temp_archive_for_reading(items).common_base() )

  def _compare_dirs(self, expected_dir, actual_dir, transform = None):
    # FIXME: How to pop this state ?
    self.maxDiff = None

    expected_files = file_find.find(expected_dir, relative = True)
    actual_files = file_find.find(actual_dir, relative = True)

    if transform:
      actual_files = [ transform(f) for f in actual_files ]

    self._unit_test.assertEqual( expected_files, actual_files )

  def test_create_basic(self):
    self.maxDiff = None

    items = temp_archive.make_temp_item_list([
      ( self.xp_path('base-1.2.3/foo.txt'), 'foo.txt\n' ),
      ( self.xp_path('base-1.2.3/bar.txt'), 'bar.txt\n' ),
    ])
    
    tmp_dir = temp_archive.write_temp_items(items)

    archive = self.make_temp_archive_for_writing()
    archive.create(tmp_dir)

    self._unit_test.assertTrue( path.isfile(archive.filename) )

    tmp_extract_dir = self._unit_test.make_temp_dir()
    archive.extract_all(tmp_extract_dir)

    self._compare_dirs(tmp_dir, tmp_extract_dir)

    file_util.remove([ tmp_dir, tmp_extract_dir])

  def test_create_base_dir(self):
    self.maxDiff = None

    items = temp_archive.make_temp_item_list([
      ( self.xp_path('base-1.2.3/foo.txt'), 'foo.txt\n' ),
      ( self.xp_path('base-1.2.3/bar.txt'), 'bar.txt\n' ),
    ])
    
    tmp_dir = temp_archive.write_temp_items(items)

    base_dir = 'foo-666'

    archive = self.make_temp_archive_for_writing()
    archive.create(tmp_dir, base_dir = base_dir)

    self._unit_test.assertTrue( path.isfile(archive.filename) )

    tmp_extract_dir = self._unit_test.make_temp_dir()
    archive.extract_all(tmp_extract_dir)

    def _remove_base_dir(f):
      return file_util.remove_head(f, base_dir)

    self._compare_dirs(tmp_dir, tmp_extract_dir, transform = _remove_base_dir)

    file_util.remove([ tmp_dir, tmp_extract_dir])

  def test_create_with_include(self):
    self.maxDiff = None
    items = temp_archive.make_temp_item_list([
      ( self.xp_path('foo.txt'), 'foo.txt\n' ),
      ( self.xp_path('bar.txt'), 'bar.txt\n' ),
      ( self.xp_path('baz.png'), 'baz.png\n' ),
      ( self.xp_path('baz2.png'), 'baz2.png\n' ),
      ( self.xp_path('apple.pdf'), 'apple.pdf\n' ),
      ( self.xp_path('kiwi.pdf'), 'kiwi.pdf\n' ),
      ( self.xp_path('durian.pdf'), 'durian.pdf\n' ),
    ])
    include = [ '*.txt' ]
    exclude = None
    expected_files = [
      self.xp_path('bar.txt'),
      self.xp_path('foo.txt'),
    ]
    actual_files = self._test_create_with_include_exclude(items, include, exclude)
    self._unit_test.assertEqual( expected_files, actual_files )

  def test_create_with_multiple_include(self):
    self.maxDiff = None
    items = temp_archive.make_temp_item_list([
      ( self.xp_path('foo.txt'), 'foo.txt\n' ),
      ( self.xp_path('bar.txt'), 'bar.txt\n' ),
      ( self.xp_path('baz.png'), 'baz.png\n' ),
      ( self.xp_path('baz2.png'), 'baz2.png\n' ),
      ( self.xp_path('apple.pdf'), 'apple.pdf\n' ),
      ( self.xp_path('kiwi.pdf'), 'kiwi.pdf\n' ),
      ( self.xp_path('durian.pdf'), 'durian.pdf\n' ),
    ])
    include = [ '*.txt', '*.png' ]
    exclude = None
    expected_files = [
      self.xp_path('bar.txt'),
      self.xp_path('baz.png'),
      self.xp_path('baz2.png'),
      self.xp_path('foo.txt'),
    ]
    actual_files = self._test_create_with_include_exclude(items, include, exclude)
    self._unit_test.assertEqual( expected_files, actual_files )

  def test_create_with_exclude(self):
    self.maxDiff = None
    items = temp_archive.make_temp_item_list([
      ( self.xp_path('foo.txt'), 'foo.txt\n' ),
      ( self.xp_path('bar.txt'), 'bar.txt\n' ),
      ( self.xp_path('baz.png'), 'baz.png\n' ),
      ( self.xp_path('baz2.png'), 'baz2.png\n' ),
      ( self.xp_path('apple.pdf'), 'apple.pdf\n' ),
      ( self.xp_path('kiwi.pdf'), 'kiwi.pdf\n' ),
      ( self.xp_path('durian.pdf'), 'durian.pdf\n' ),
    ])
    include = None
    exclude = [ '*.txt' ]
    expected_files = [
      self.xp_path('apple.pdf'),
      self.xp_path('baz.png'),
      self.xp_path('baz2.png'),
      self.xp_path('durian.pdf'),
      self.xp_path('kiwi.pdf'),
    ]
    actual_files = self._test_create_with_include_exclude(items, include, exclude)
    self._unit_test.assertEqual( expected_files, actual_files )

  def test_create_with_multiple_exclude(self):
    self.maxDiff = None
    items = temp_archive.make_temp_item_list([
      ( self.xp_path('foo.txt'), 'foo.txt\n' ),
      ( self.xp_path('bar.txt'), 'bar.txt\n' ),
      ( self.xp_path('baz.png'), 'baz.png\n' ),
      ( self.xp_path('baz2.png'), 'baz2.png\n' ),
      ( self.xp_path('apple.pdf'), 'apple.pdf\n' ),
      ( self.xp_path('kiwi.pdf'), 'kiwi.pdf\n' ),
      ( self.xp_path('durian.pdf'), 'durian.pdf\n' ),
    ])
    include = None
    exclude = [ '*.txt', '*.png' ]
    expected_files = [
      self.xp_path('apple.pdf'),
      self.xp_path('durian.pdf'),
      self.xp_path('kiwi.pdf'),
    ]
    actual_files = self._test_create_with_include_exclude(items, include, exclude)
    self._unit_test.assertEqual( expected_files, actual_files )

  def test_create_with_include_and_exclude(self):
    self.maxDiff = None
    items = temp_archive.make_temp_item_list([
      ( self.xp_path('base-1.2.3/foo.txt'), 'foo.txt\n' ),
      ( self.xp_path('base-1.2.3/bar.txt'), 'bar.txt\n' ),
      ( self.xp_path('base-1.2.3/baz.png'), 'baz.png\n' ),
      ( self.xp_path('base-1.2.3/baz2.png'), 'baz2.png\n' ),
      ( self.xp_path('base-1.2.3/apple.pdf'), 'apple.pdf\n' ),
      ( self.xp_path('base-1.2.3/kiwi.pdf'), 'kiwi.pdf\n' ),
      ( self.xp_path('base-1.2.3/durian.pdf'), 'durian.pdf\n' ),
    ])
    include = [ '*.pdf' ]
    exclude = [ '*kiwi.pdf' ]
    expected_files = [
      self.xp_path('base-1.2.3/apple.pdf'),
      self.xp_path('base-1.2.3/durian.pdf'),
    ]
    actual_files = self._test_create_with_include_exclude(items, include, exclude)
    self._unit_test.assertEqual( expected_files, actual_files )

  def _test_create_with_include_exclude(self, items, include, exclude):
    tmp_dir = temp_archive.write_temp_items(items)
    archive = self.make_temp_archive_for_writing()
    archive.create(tmp_dir, include = include, exclude = exclude)
    self._unit_test.assertTrue( path.isfile(archive.filename) )
    tmp_extract_dir = self._unit_test.make_temp_dir()
    archive.extract_all(tmp_extract_dir)
    actual_files = file_find.find(tmp_extract_dir, relative = True)
    file_util.remove([ tmp_dir, tmp_extract_dir])
    return actual_files

  def xtest_checksum(self):
    items = temp_archive.make_temp_item_list([
      ( self.xp_path('foo.txt'), 'foo.txt\n' ),
      ( self.xp_path('bar.txt'), 'bar.txt\n' ),
      ( self.xp_path('baz.png'), 'baz.png\n' ),
      ( self.xp_path('baz2.png'), 'baz2.png\n' ),
      ( self.xp_path('apple.pdf'), 'apple.pdf\n' ),
      ( self.xp_path('kiwi.pdf'), 'kiwi.pdf\n' ),
      ( self.xp_path('durian.pdf'), 'durian.pdf\n' ),
    ])
    tmp_dir = temp_archive.write_temp_items(items)
    archive1 = self.make_temp_archive_for_writing()
    archive1.create(tmp_dir)
    checksum1 = file_util.checksum('sha256', archive1.filename)
    
    archive2 = self.make_temp_archive_for_writing()
    archive2.create(tmp_dir)
    checksum2 = file_util.checksum('sha256', archive2.filename)

    self._unit_test.assertEqual( checksum1, checksum2 )

  @classmethod
  def xp_path(clazz, s, pathsep = ':', sep = '/'):
    result = s.replace(pathsep, os.pathsep)
    result = result.replace(sep, os.sep)
    return result

  @classmethod
  def p(clazz, s, pathsep = ':', sep = '/'):
    return clazz.xp_path(s, pathsep = pathsep, sep = sep)
    

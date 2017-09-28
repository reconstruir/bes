#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, os.path as path
from abc import abstractmethod
from collections import namedtuple

from bes.common import algorithm
from bes.fs import file_find, file_util, tar_util, temp_file
from bes.match import matcher_multiple_filename, matcher_always_false, matcher_always_true, matcher_util

class archive(object):
  'An archive interface.'

  Item = namedtuple('Item', [ 'filename', 'arcname' ])

  def __init__(self, filename):
    self.filename = filename

  @abstractmethod
  def is_valid(self):
    pass

  @abstractmethod
  def members(self):
    pass

  @abstractmethod
  def extract_members(self, members, dest_dir, base_dir = None,
                      strip_common_base = False, strip_head = None,
                      include = None, exclude = None):
    pass

  @abstractmethod
  def create(self, root_dir, base_dir = None,
             extra_items = None,
             include = None, exclude = None):
    pass

  def extract(self, dest_dir, base_dir = None,
              strip_common_base = False, strip_head = None,
              include = None, exclude = None):
    return self.extract_members(self.members(),
                                dest_dir,
                                base_dir = base_dir,
                                strip_common_base = strip_common_base,
                                strip_head = strip_head,
                                include = include, exclude = exclude)

  def extract_member_to_string(self, member):
    tmp_dir = temp_file.make_temp_dir()
    tmp_member = path.join(tmp_dir, member)
    self.extract_members([ member ], tmp_dir)
    if not path.exists(tmp_member):
      raise RuntimeError('Failed to extract member: %s' % (member))
    if not path.isfile(tmp_member):
      raise RuntimeError('Member is not a file: %s' % (member))
    result = file_util.read(tmp_member)
    file_util.remove(tmp_dir)
    return result

  # FIXME: cut-n-paste with above
  def extract_member_to_file(self, member, filename):
    tmp_dir = temp_file.make_temp_dir()
    tmp_member = path.join(tmp_dir, member)
    self.extract_members([ member ], tmp_dir)
    if not path.exists(tmp_member):
      raise RuntimeError('Failed to extract member: %s' % (member))
    if not path.isfile(tmp_member):
      raise RuntimeError('Member is not a file: %s' % (member))
    file_util.rename(tmp_member, filename)

  def common_base(self):
    'Return a common base dir for the archive or None if no common base exists.'
    return self._common_base_for_members(self.members())

  @classmethod
  def _normalize_members(clazz, members):
    'Return a sorted and unique list of members.'
    return sorted(algorithm.unique(members))

  # Some archives have some dumb members that are immaterial to common base
  COMMON_BASE_MEMBERS_EXCLUDE = [ '.' ]

  @classmethod
  def _common_base_for_members(clazz, members):
    'Return a common base dir for the given members or None if no common base exists.'
    def _path_base(p):
      return file_util.strip_sep(path.normpath(p).split(os.sep)[0])
    bases = [ _path_base(member) for member in members if member not in clazz.COMMON_BASE_MEMBERS_EXCLUDE ]

    common_base = algorithm.unique(bases)
    if len(common_base) == 1:
      return common_base[0] or None
    return None

  @classmethod
  def _find(clazz, root_dir, base_dir, extra_items, include, exclude):
    files = file_find.find(root_dir, relative = True, file_type = file_find.FILE | file_find.LINK)
    items = []

    if include:
      include_matcher = matcher_multiple_filename(include)
    else:
      include_matcher = matcher_always_true()

    if exclude:
      exclude_matcher = matcher_multiple_filename(exclude)
    else:
      exclude_matcher = matcher_always_false()

    for f in files:
      filename = path.join(root_dir, f)
      if base_dir:
        arcname = path.join(base_dir, f)
      else:
        arcname = f

      should_include = include_matcher.match(arcname)
      should_exclude = exclude_matcher.match(arcname)

      if should_include and not should_exclude:
        items.append(clazz.Item(filename, arcname))

    return items + (extra_items or [])

  @classmethod
  def _determine_dest_dir(clazz, dest_dir, base_dir):
    if base_dir:
      dest_dir = path.join(dest_dir, base_dir)
    else:
      dest_dir = dest_dir
    file_util.mkdir(dest_dir)
    return dest_dir

  def _handle_extract_strip_common_base(self, members, strip_common_base, strip_head, dest_dir):
    if strip_common_base:
      common_base = self._common_base_for_members(members)
      if common_base:
        from_dir = path.join(dest_dir, common_base)
        tar_util.copy_tree_with_tar(from_dir, dest_dir)
        file_util.remove(from_dir)
    if strip_head:
      from_dir = path.join(dest_dir, strip_head)
      tar_util.copy_tree_with_tar(from_dir, dest_dir)
      file_util.remove(from_dir)
      
  def _pre_create(self):
    'Setup some stuff before create() is called.'
    d = path.dirname(self.filename)
    if d:
      file_util.mkdir(d)

  @classmethod
  def _filter_for_extract(clazz, members, include, exclude):
    return matcher_util.match_filenames(members, include, exclude)

from .temp_archive import temp_archive
from bes.fs import temp_file

class archive_base_common(object):
  'Superclass for archive unit tests for which logic is shared regardless of the archive type.'

  @abstractmethod
  def make_archive(self, filename):
    pass

  def make_temp_archive_for_reading(self, items, archive_type = None):
    archive_type = archive_type or self.default_archive_type
    assert archive_type
    tmp_archive = temp_archive.make_temp_archive(items, archive_type)
    return self.make_archive(tmp_archive.filename)

  def make_temp_archive_for_writing(self):
    tmp_archive = temp_file.make_temp_file(suffix = '.' + self.default_archive_type, delete = False)
    return self.make_archive(tmp_archive)

  def test_members(self):
    assert self.default_archive_type
    tmp_tar = temp_archive.make_temp_archive([ temp_archive.Item('foo.txt', 'foo.txt\n') ], self.default_archive_type)
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

  def test_extract_with_base_dir(self):
    assert self.default_archive_type
    items = temp_archive.make_temp_item_list([
      ( 'foo.txt', 'foo.txt\n' ),
    ])
    tmp_archive = self.make_temp_archive_for_reading(items)
    tmp_dir = temp_file.make_temp_dir()
    base_dir = 'base-1.2.3'
    tmp_archive.extract(tmp_dir, base_dir = base_dir)
    self.assertTrue( path.isfile(path.join(tmp_dir, base_dir, 'foo.txt')) )

  def test_extract_with_strip_common_base(self):
    assert self.default_archive_type
    base_dir_to_strip = 'base-1.2.3'

    items = temp_archive.make_temp_item_list([
      ( 'foo.txt', 'foo.txt\n' ),
    ])
    items = temp_archive.add_base_dir(items, base_dir_to_strip)
    tmp_archive = self.make_temp_archive_for_reading(items)
    tmp_dir = temp_file.make_temp_dir()
    tmp_archive.extract(tmp_dir, strip_common_base = True)
    self.assertTrue( path.isfile(path.join(tmp_dir, 'foo.txt')) )

  def test_extract_with_base_dir_and_strip_common_base(self):
    assert self.default_archive_type
    base_dir_to_strip = 'base-1.2.3'
    items = temp_archive.make_temp_item_list([
      ( 'foo.txt', 'foo.txt\n' ),
    ])
    items = temp_archive.add_base_dir(items, base_dir_to_strip)
    base_dir_to_add = 'added-6.6.6'
    tmp_archive = self.make_temp_archive_for_reading(items)
    tmp_dir = temp_file.make_temp_dir()
    tmp_archive.extract(tmp_dir, base_dir = base_dir_to_add, strip_common_base = True)
    self.assertTrue( path.isfile(path.join(tmp_dir, base_dir_to_add, 'foo.txt')) )

  def test_extract_with_strip_head(self):
    assert self.default_archive_type

    items = temp_archive.make_temp_item_list([
      ( 'foo/apple.txt', 'apple.txt\n' ),
      ( 'foo/durian.txt', 'durian.txt\n' ),
      ( 'foo/kiwi.txt', 'kiwi.txt\n' ),
      ( 'metadata/db.json', '{}\n' ),
    ])
    tmp_archive = self.make_temp_archive_for_reading(items)
    tmp_dir = temp_file.make_temp_dir()
    tmp_archive.extract(tmp_dir, strip_head = 'foo')

    actual_files = file_find.find(tmp_dir, relative = True)

    expected_files = [
      'apple.txt',
      'durian.txt',
      'kiwi.txt',
      'metadata/db.json',
    ]

    self.assertEqual( expected_files, actual_files )

  def test_extract_with_strip_common_base_and_strip_head(self):
    assert self.default_archive_type

    items = temp_archive.make_temp_item_list([
      ( 'base-1.2.3/foo/apple.txt', 'apple.txt\n' ),
      ( 'base-1.2.3/foo/durian.txt', 'durian.txt\n' ),
      ( 'base-1.2.3/foo/kiwi.txt', 'kiwi.txt\n' ),
      ( 'base-1.2.3/metadata/db.json', '{}\n' ),
    ])
    tmp_archive = self.make_temp_archive_for_reading(items)
    tmp_dir = temp_file.make_temp_dir()
    tmp_archive.extract(tmp_dir, strip_common_base = True, strip_head = 'foo')

    actual_files = file_find.find(tmp_dir, relative = True)

    expected_files = [
      'apple.txt',
      'durian.txt',
      'kiwi.txt',
      'metadata/db.json',
    ]

    self.assertEqual( expected_files, actual_files )

  def test_extract_overlap(self):
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
    tmp_archive1.extract(tmp_dir)
    tmp_archive2.extract(tmp_dir)

    actual_files = file_find.find(tmp_dir, relative = True)

    expected_files = [
      'base-1.2.3/bar.txt',
      'base-1.2.3/foo.txt',
      'base-1.2.3/kiwi.txt',
      'base-1.2.3/orange.txt',
    ]

    self.assertEqual( expected_files, actual_files )

  def test_extract_overlap_with_base_dir(self):
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
    tmp_archive1.extract(tmp_dir, base_dir = base_dir)
    tmp_archive2.extract(tmp_dir, base_dir = base_dir)

    actual_files = file_find.find(tmp_dir, relative = True)

    expected_files = [
      'foo-6.6.6/base-1.2.3/bar.txt',
      'foo-6.6.6/base-1.2.3/foo.txt',
      'foo-6.6.6/base-1.2.3/kiwi.txt',
      'foo-6.6.6/base-1.2.3/orange.txt',
    ]

    self.assertEqual( expected_files, actual_files )

  def test_extract_overlap_with_base_dir_and_strip_common_base(self):
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
    tmp_archive1.extract(tmp_dir, base_dir = base_dir, strip_common_base = True)
    tmp_archive2.extract(tmp_dir, base_dir = base_dir, strip_common_base = True)

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
    actual_files = self.__test_extract_with_include_exclude(items, include, exclude)
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
    actual_files = self.__test_extract_with_include_exclude(items, include, exclude)
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
    actual_files = self.__test_extract_with_include_exclude(items, include, exclude)

    expected_files = [
      'foo/apple.txt',
      'foo/kiwi.txt',
    ]
    self.assertEqual( expected_files, actual_files )

  def __test_extract_with_include_exclude(self, items, include, exclude):
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
    self.assertEqual( 'apple.txt\n', tmp_archive.extract_member_to_string('foo/apple.txt') )
    self.assertEqual( '{}\n', tmp_archive.extract_member_to_string('metadata/db.json') )

  def __test_extract_with_members(self, items, members,
                                  base_dir = None,
                                  strip_common_base = False,
                                  strip_head = None,
                                  include = None,
                                  exclude = None):
    tmp_archive = self.make_temp_archive_for_reading(items)
    tmp_dir = temp_file.make_temp_dir()
    tmp_archive.extract_members(members,
                                tmp_dir,
                                base_dir = base_dir,
                                strip_common_base = strip_common_base,
                                strip_head = strip_head,
                                include = include,
                                exclude = exclude)
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
    actual_files = self.__test_extract_with_members(items, members)
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
    archive.extract(tmp_extract_dir)

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
    archive.extract(tmp_extract_dir)

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
    actual_files = self.__test_create_with_include_exclude(items, include, exclude)
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
    actual_files = self.__test_create_with_include_exclude(items, include, exclude)
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
    actual_files = self.__test_create_with_include_exclude(items, include, exclude)
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
    actual_files = self.__test_create_with_include_exclude(items, include, exclude)
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
    actual_files = self.__test_create_with_include_exclude(items, include, exclude)
    self.assertEqual( expected_files, actual_files )

  def __test_create_with_include_exclude(self, items, include, exclude):
    tmp_dir = temp_archive.write_temp_items(items)
    archive = self.make_temp_archive_for_writing()
    archive.create(tmp_dir, include = include, exclude = exclude)
    self.assertTrue( path.isfile(archive.filename) )
    tmp_extract_dir = temp_file.make_temp_dir()
    archive.extract(tmp_extract_dir)
    actual_files = file_find.find(tmp_extract_dir, relative = True)
    file_util.remove([ tmp_dir, tmp_extract_dir])
    return actual_files

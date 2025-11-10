#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from collections import namedtuple

from bes.files.match.bf_file_matcher import bf_file_matcher
from bes.files.find.bf_file_scanner import bf_file_scanner
from bes.files.find.bf_file_scanner_options import bf_file_scanner_options
from bes.files.bf_entry import bf_entry
from bes.files.bf_entry_list import bf_entry_list
from bes.fs.testing.temp_content import temp_content
from bes.system.log import logger

from bes.testing.unit_test import unit_test
from bes.testing.unit_test_function_skip import unit_test_function_skip

class test_bf_file_scanner(unit_test):

  _log = logger('bf_file_scanner')
  
  @classmethod
  def _make_temp_content(clazz, items):
    return temp_content.write_items_to_temp_dir(items, delete = not clazz.DEBUG)

  _scan_result = namedtuple('_scan_result', 'tmp_dir, entries, relative_filenames, absolute_filenames, sorted_relative_filenames, sorted_absolute_filenames, stats')
  def _scan(self, items, **options):
    finder_options = bf_file_scanner_options(**options)
    tmp_dir = self._make_temp_content(items)
    f = bf_file_scanner(options = finder_options)
    result = f.scan(tmp_dir)
    entries = result.entries

    relative_filenames = entries.relative_filenames(False)
    absolute_filenames = entries.absolute_filenames(False)

    sorted_relative_filenames = entries.relative_filenames(True)
    sorted_absolute_filenames = entries.absolute_filenames(True)
    return self._scan_result(tmp_dir,
                             entries,
                             relative_filenames,
                             absolute_filenames,
                             sorted_relative_filenames,
                             sorted_absolute_filenames,
                             result.stats)

  def test_scan_with_no_options(self):
    content = [
      'file foo.txt "foo.txt\n"',
      'file subdir/bar.txt "bar.txt\n"',
      'file subdir/subberdir/baz.txt "baz.txt\n"',
      'file emptyfile.txt',
      'dir emptydir',
    ]
    self.assert_filename_list_equal( [
      'emptyfile.txt',
      'foo.txt',
      'subdir/bar.txt',
      'subdir/subberdir/baz.txt'
    ], self._scan(content).sorted_relative_filenames )

  def test_scan_absolute(self):
    content = [
      'file foo.txt "foo.txt\n"',
      'file subdir/bar.txt "bar.txt\n"',
      'file subdir/subberdir/baz.txt "baz.txt\n"',
      'file emptyfile.txt',
      'dir emptydir',
    ]
    rv = self._scan(content)
    expected_relative = [
      'emptyfile.txt',
      'foo.txt',
      'subdir/bar.txt',
      'subdir/subberdir/baz.txt'
    ]    
    expected = [ path.join(rv.tmp_dir, f) for f in expected_relative ]
    self.assert_filename_list_equal( expected, rv.sorted_absolute_filenames )

  def test_scan_with_files_only(self):
    content = [
      'file foo.txt "foo.txt\n"',
      'file subdir/bar.txt "bar.txt\n"',
      'file subdir/subberdir/baz.txt "baz.txt\n"',
      'file emptyfile.txt',
      'dir emptydir',
    ]
    self.assert_filename_list_equal( [
      'emptyfile.txt',
      'foo.txt',
      'subdir/bar.txt',
      'subdir/subberdir/baz.txt'
    ], self._scan(content, file_type = 'file').sorted_relative_filenames )

  def test_scan_with_dirs_only(self):
    content = [
      'file foo.txt "foo.txt\n"',
      'file subdir/bar.txt "bar.txt\n"',
      'file subdir/subberdir/baz.txt "baz.txt\n"',
      'file emptyfile.txt',
      'dir emptydir',
    ]
    self.assert_filename_list_equal( [
      'emptydir',
      'subdir',
      'subdir/subberdir',
    ], self._scan(content, file_type = 'dir').sorted_relative_filenames )

  def test_scan_with_max_depth(self):
    self.maxDiff = None
    content = [
      'file 1a.f',
      'file 1b.f',
      'file 1.d/2a.f',
      'file 1.d/2b.f',
      'file 1.d/2.d/3a.f',
      'file 1.d/2.d/3b.f',
      'file 1.d/2.d/3.d/4a.f',
      'file 1.d/2.d/3.d/4b.f',
      'file 1.d/2.d/3.d/4.d/5a.f',
      'file 1.d/2.d/3.d/4.d/5b.f',
    ]

    self.assert_filename_list_equal( sorted([
      '1a.f',
      '1b.f',
    ]), self._scan(content, max_depth = 1).sorted_relative_filenames )
    self.assert_filename_list_equal( sorted([
      '1a.f',
      '1b.f',
      '1.d/2a.f',
      '1.d/2b.f',
    ]), self._scan(content, max_depth = 2).sorted_relative_filenames )
    self.assert_filename_list_equal( sorted([
      '1a.f',
      '1b.f',
      '1.d/2a.f',
      '1.d/2b.f',
      '1.d/2.d/3a.f',
      '1.d/2.d/3b.f',
    ]), self._scan(content, max_depth = 3).sorted_relative_filenames )
    self.assert_filename_list_equal( sorted([
      '1a.f',
      '1b.f',
      '1.d/2a.f',
      '1.d/2b.f',
      '1.d/2.d/3a.f',
      '1.d/2.d/3b.f',
      '1.d/2.d/3.d/4a.f',
      '1.d/2.d/3.d/4b.f',
    ]), self._scan(content, max_depth = 4).sorted_relative_filenames )
    self.assert_filename_list_equal( sorted([
      '1a.f',
      '1b.f',
      '1.d/2a.f',
      '1.d/2b.f',
      '1.d/2.d/3a.f',
      '1.d/2.d/3b.f',
      '1.d/2.d/3.d/4a.f',
      '1.d/2.d/3.d/4b.f',
      '1.d/2.d/3.d/4.d/5a.f',
      '1.d/2.d/3.d/4.d/5b.f',
    ]), self._scan(content, max_depth = 5).sorted_relative_filenames )

  def test_scan_with_min_depth(self):
    self.maxDiff = None
    content = [
      'file 1a.f',
      'file 1b.f',
      'file 1.d/2a.f',
      'file 1.d/2b.f',
      'file 1.d/2.d/3a.f',
      'file 1.d/2.d/3b.f',
      'file 1.d/2.d/3.d/4a.f',
      'file 1.d/2.d/3.d/4b.f',
      'file 1.d/2.d/3.d/4.d/5a.f',
      'file 1.d/2.d/3.d/4.d/5b.f',
    ]

    self.assert_filename_list_equal( sorted([
      '1a.f',
      '1b.f',
      '1.d/2a.f',
      '1.d/2b.f',
      '1.d/2.d/3a.f',
      '1.d/2.d/3b.f',
      '1.d/2.d/3.d/4a.f',
      '1.d/2.d/3.d/4b.f',
      '1.d/2.d/3.d/4.d/5a.f',
      '1.d/2.d/3.d/4.d/5b.f',
    ]), self._scan(content, min_depth = 1).sorted_relative_filenames )
    self.assert_filename_list_equal( sorted([
      '1.d/2a.f',
      '1.d/2b.f',
      '1.d/2.d/3a.f',
      '1.d/2.d/3b.f',
      '1.d/2.d/3.d/4a.f',
      '1.d/2.d/3.d/4b.f',
      '1.d/2.d/3.d/4.d/5a.f',
      '1.d/2.d/3.d/4.d/5b.f',
    ]), self._scan(content, min_depth = 2).sorted_relative_filenames )
    self.assert_filename_list_equal( sorted([
      '1.d/2.d/3a.f',
      '1.d/2.d/3b.f',
      '1.d/2.d/3.d/4a.f',
      '1.d/2.d/3.d/4b.f',
      '1.d/2.d/3.d/4.d/5a.f',
      '1.d/2.d/3.d/4.d/5b.f',
    ]), self._scan(content, min_depth = 3).sorted_relative_filenames )
    self.assert_filename_list_equal( sorted([
      '1.d/2.d/3.d/4a.f',
      '1.d/2.d/3.d/4b.f',
      '1.d/2.d/3.d/4.d/5a.f',
      '1.d/2.d/3.d/4.d/5b.f',
    ]), self._scan(content, min_depth = 4).sorted_relative_filenames )
    self.assert_filename_list_equal( sorted([
      '1.d/2.d/3.d/4.d/5a.f',
      '1.d/2.d/3.d/4.d/5b.f',
    ]), self._scan(content, min_depth = 5).sorted_relative_filenames )
    self.assert_filename_list_equal( sorted([]), self._scan(content, min_depth = 6).sorted_relative_filenames )

  def test_scan_with_min_and_max_depth(self):
    self.maxDiff = None
    content = [
      'file 1a.f',
      'file 1b.f',
      'file 1.d/2a.f',
      'file 1.d/2b.f',
      'file 1.d/2.d/3a.f',
      'file 1.d/2.d/3b.f',
      'file 1.d/2.d/3.d/4a.f',
      'file 1.d/2.d/3.d/4b.f',
      'file 1.d/2.d/3.d/4.d/5a.f',
      'file 1.d/2.d/3.d/4.d/5b.f',
    ]

    self.assert_filename_list_equal( sorted([
      '1a.f',
      '1b.f',
      '1.d/2a.f',
      '1.d/2b.f',
    ]), self._scan(content, min_depth = 1, max_depth = 2).sorted_relative_filenames )
    self.assert_filename_list_equal( sorted([
      '1.d/2a.f',
      '1.d/2b.f',
      '1.d/2.d/3a.f',
      '1.d/2.d/3b.f',
    ]), self._scan(content, min_depth = 2, max_depth = 3).sorted_relative_filenames )
    self.assert_filename_list_equal( sorted([
      '1.d/2a.f',
      '1.d/2b.f',
    ]), self._scan(content, min_depth = 2, max_depth = 2).sorted_relative_filenames )
    self.assert_filename_list_equal( sorted([
      '1a.f',
      '1b.f',
    ]), self._scan(content, min_depth = 1, max_depth = 1).sorted_relative_filenames )

  @unit_test_function_skip.skip_if_not_unix()
  def test_scan_with_broken_symlink(self):
    content = [
      'file fruit/kiwi.fruit',
      'file fruit/lemon.fruit',
      'file fruit/strawberry.fruit',
      'file fruit/blueberry.fruit',
      'file cheese/brie.cheese',
      'link cheese/cheddar.cheese "/foo/notthere"',
    ]
    self.assert_filename_list_equal( [
      'cheese/brie.cheese',
      'fruit/blueberry.fruit',
      'fruit/kiwi.fruit',
      'fruit/lemon.fruit',
      'fruit/strawberry.fruit',
    ], self._scan(content).sorted_relative_filenames )

  @unit_test_function_skip.skip_if_not_unix()
  def test_scan_with_broken_symlink_without_ignore_broken_links(self):
    content = [
      'file fruit/kiwi.fruit',
      'file fruit/lemon.fruit',
      'file fruit/strawberry.fruit',
      'file fruit/blueberry.fruit',
      'file cheese/brie.cheese',
      'link cheese/cheddar.cheese "/foo/notthere"',
    ]
    self.assert_filename_list_equal( [
      'cheese/brie.cheese',
      'cheese/cheddar.cheese',
      'fruit/blueberry.fruit',
      'fruit/kiwi.fruit',
      'fruit/lemon.fruit',
      'fruit/strawberry.fruit',
    ], self._scan(content, ignore_broken_links = False).sorted_relative_filenames )

  @unit_test_function_skip.skip_if_not_unix()
  def test_scan_with_broken_symlink_with_ignore_broken_links(self):
    content = [
      'file fruit/kiwi.fruit',
      'file fruit/lemon.fruit',
      'file fruit/strawberry.fruit',
      'file fruit/blueberry.fruit',
      'file cheese/brie.cheese',
      'link cheese/cheddar.cheese "/foo/notthere"',
    ]
    self.assert_filename_list_equal( [
      'cheese/brie.cheese',
      'fruit/blueberry.fruit',
      'fruit/kiwi.fruit',
      'fruit/lemon.fruit',
      'fruit/strawberry.fruit',
    ], self._scan(content, ignore_broken_links = True).sorted_relative_filenames )
    
  def test_scan_with_stop_after(self):
    content = [
      'file a/kiwi.txt',
      'file b/kiwi.txt',
      'file c/kiwi.txt',
    ]
    self.assert_filename_list_equal( [
      'a/kiwi.txt',
    ], self._scan(content, stop_after = 1).sorted_relative_filenames )

  def test_scan_with_multiple_dirs(self):
    content = [
      'file 1/a/fruit/kiwi.fruit',
      'file 1/a/fruit/lemon.fruit',
      'file 1/a/fruit/strawberry.fruit',
      'file 1/a/fruit/blueberry.fruit',
      'file 1/a/cheese/brie.cheese',
      'file 1/a/cheese/cheddar.cheese',
      'file 2/b/fruit/kiwi.fruit',
      'file 2/b/fruit/lemon.fruit',
      'file 2/b/fruit/strawberry.fruit',
      'file 2/b/fruit/blueberry.fruit',
      'file 2/b/cheese/brie.cheese',
      'file 2/b/cheese/cheddar.cheese',
      'file 3/c/fruit/kiwi.fruit',
      'file 3/c/fruit/lemon.fruit',
      'file 3/c/fruit/strawberry.fruit',
      'file 3/c/fruit/blueberry.fruit',
      'file 3/c/cheese/brie.cheese',
      'file 3/c/cheese/cheddar.cheese',
    ]
    tmp_dir = self._make_temp_content(content)
    f = bf_file_scanner()
    result = f.scan([
      path.join(tmp_dir, '1'),
      path.join(tmp_dir, '2'),
      path.join(tmp_dir, '3'),
    ])
    actual = result.entries.relative_filenames(True)
    self.assert_filename_list_equal( [
      'a/cheese/brie.cheese',
      'a/cheese/cheddar.cheese',
      'a/fruit/blueberry.fruit',
      'a/fruit/kiwi.fruit',
      'a/fruit/lemon.fruit',
      'a/fruit/strawberry.fruit',
      'b/cheese/brie.cheese',
      'b/cheese/cheddar.cheese',
      'b/fruit/blueberry.fruit',
      'b/fruit/kiwi.fruit',
      'b/fruit/lemon.fruit',
      'b/fruit/strawberry.fruit',
      'c/cheese/brie.cheese',
      'c/cheese/cheddar.cheese',
      'c/fruit/blueberry.fruit',
      'c/fruit/kiwi.fruit',
      'c/fruit/lemon.fruit',
      'c/fruit/strawberry.fruit',
    ], actual )
    
  def test_scan_with_stats_file_only(self):
    content = [
      'file .git/HEAD "x"',
      'file .git/config "x"',
      'file .git/description "x"',
      'file .git/hooks/applypatch-msg.sample "x"',
      'file .git/info/exclude "x"',
      'file kiwi.git "x"',
      'file a/b/c/foo.txt "x"',
      'file d/e/bar.txt "x"',
    ]
    result = self._scan(content, file_type = 'FILE')
    self.assert_filename_list_equal( [
      '.git/HEAD',
      '.git/config',
      '.git/description',
      '.git/hooks/applypatch-msg.sample',
      '.git/info/exclude',
      'a/b/c/foo.txt',
      'd/e/bar.txt',
      'kiwi.git',
    ], result.sorted_relative_filenames )
    self.assertEqual( 8, result.stats.num_checked )
    self.assertEqual( 8, result.stats.num_files_checked )
    self.assertEqual( 0, result.stats.num_dirs_checked )
    self.assertEqual( 3, result.stats.depth )

  def test_scan_with_stats_file_only_with_dir_walk_matcher(self):
    content = [
      'file .git/HEAD "x"',
      'file .git/config "x"',
      'file .git/description "x"',
      'file .git/hooks/applypatch-msg.sample "x"',
      'file .git/info/exclude "x"',
      'file kiwi.git "x"',
      'file a/b/c/foo.txt "x"',
      'file d/e/bar.txt "x"',
    ]
    walk_dir_matcher = bf_file_matcher()
    walk_dir_matcher.add_item_fnmatch('.git',
                                      file_type = 'dir',
                                      path_type = 'basename',
                                      negate = True)
    result = self._scan(content,
                        file_type = 'FILE',
                        walk_dir_matcher = walk_dir_matcher,
                        walk_dir_match_type = 'all')
    self.assert_filename_list_equal( [
      'a/b/c/foo.txt',
      'd/e/bar.txt',
      'kiwi.git',
    ], result.sorted_relative_filenames )
    self.assertEqual( 3, result.stats.num_checked )
    self.assertEqual( 3, result.stats.num_files_checked )
    self.assertEqual( 0, result.stats.num_dirs_checked )
    self.assertEqual( 3, result.stats.depth )
    
  def xtest_scan_with_stats_dir_only(self):
    content = [
      'file .git/HEAD "x"',
      'file .git/config "x"',
      'file .git/description "x"',
      'file .git/hooks/applypatch-msg.sample "x"',
      'file .git/info/exclude "x"',
      'file kiwi.git "x"',
      'file a/b/c/foo.txt "x"',
      'file d/e/bar.txt "x"',
    ]
    result = self._scan(content,
                        file_type = 'DIR',
                        match_type = 'all')
    self.assert_filename_list_equal( [
      '.git',
      '.git/hooks',
      '.git/info',
      'a',
      'a/b',
      'a/b/c',
      'd',
      'd/e',
    ], result.sorted_relative_filenames )
    self.assertEqual( 8, result.stats.num_checked )

    self.assertEqual( 0, result.stats.num_dirs_checked )
    self.assertEqual( 3, result.stats.depth )

  def test_scan_with_custom_entry_type(self):
    class _test_bf_entry(bf_entry):
      pass
    content = [
      'file foo.txt "foo.txt\n"',
    ]
    result = self._scan(content, file_type = 'file',
                        file_entry_class = _test_bf_entry,
                        dir_entry_class = _test_bf_entry)
    self.assert_filename_list_equal( [
      'foo.txt',
    ], result.sorted_relative_filenames )
    self.assertEqual( type(result.entries[0]), _test_bf_entry )

  def test_scan_with_ignore_filename_basic(self):
    content = [
      'file fruit/kiwi.fruit',
      'file fruit/lemon.fruit',
      'file fruit/strawberry.fruit',
      'file fruit/blueberry.fruit',
      'file cheese/brie.cheese',
      'file cheese/cheddar.cheese',
      'file cheese/.testing_test_ignore "cheddar.cheese\n" 644',
    ]
    self.assert_filename_list_equal( [
      'cheese/brie.cheese',
      'fruit/blueberry.fruit',
      'fruit/kiwi.fruit',
      'fruit/lemon.fruit',
      'fruit/strawberry.fruit',
    ], self._scan(content, ignore_filename = '.testing_test_ignore').sorted_relative_filenames )

  def test_scan_with_ignore_filename_one_level_up(self):
    content = [
      'file fruit/kiwi.fruit',
      'file fruit/lemon.fruit',
      'file fruit/strawberry.fruit',
      'file fruit/blueberry.fruit',
      'file cheese/brie.cheese',
      'file cheese/cheddar.cheese',
      'file .testing_test_ignore "cheddar.cheese\n" 644',
    ]
    self.assert_filename_list_equal( [
      'cheese/brie.cheese',
      'fruit/blueberry.fruit',
      'fruit/kiwi.fruit',
      'fruit/lemon.fruit',
      'fruit/strawberry.fruit',
    ], self._scan(content, ignore_filename = '.testing_test_ignore').sorted_relative_filenames )
    
  def test_scan_with_resource_forks(self):
    content = [
      'file fruit/kiwi.fruit',
      'file fruit/lemon.fruit',
      'resource_fork fruit/._lemon.fruit',
    ]
    tmp_dir = self._make_temp_content(content)
    f = bf_file_scanner()
    self.assert_filename_list_equal( [
      'fruit/._lemon.fruit',
      'fruit/kiwi.fruit',
      'fruit/lemon.fruit',
    ], self._scan(content, include_resource_forks = True).sorted_relative_filenames )
    
  def test_scan_without_resource_forks(self):
    content = [
      'file fruit/kiwi.fruit',
      'file fruit/lemon.fruit',
      'resource_fork fruit/._lemon.fruit',
    ]
    tmp_dir = self._make_temp_content(content)
    f = bf_file_scanner()
    self.assert_filename_list_equal( [
      'fruit/kiwi.fruit',
      'fruit/lemon.fruit',
    ], self._scan(content, include_resource_forks = False).sorted_relative_filenames )
    
if __name__ == '__main__':
  unit_test.main()

#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from collections import namedtuple

from bes.files.match.bf_file_matcher import bf_file_matcher
from bes.files.match.bf_file_matcher_options import bf_file_matcher_options
from bes.files.find.bf_file_finder import bf_file_finder
from bes.files.find.bf_file_finder_options import bf_file_finder_options
from bes.files.bf_entry import bf_entry
from bes.files.bf_entry_list import bf_entry_list
from bes.fs.testing.temp_content import temp_content
from bes.system.log import logger

from bes.testing.unit_test import unit_test

class test_bf_file_finder(unit_test):

  _log = logger('bf_file_finder')
  
  @classmethod
  def _make_temp_content(clazz, items):
    return temp_content.write_items_to_temp_dir(items, delete = not clazz.DEBUG)

  _find_result = namedtuple('_find_result', 'tmp_dir, entries, filenames, sorted_filenames, stats')
  def _find(self, items, **options):
    finder_options = bf_file_finder_options(**options)
    tmp_dir = self._make_temp_content(items)
    f = bf_file_finder(options = finder_options)
    entries = f.find(tmp_dir)
    filenames = entries.filenames()
    sorted_filenames = sorted(filenames)
    return self._find_result(tmp_dir, entries, filenames, sorted_filenames, None)

  def _find_with_stats(self, items, **options):
    finder_options = bf_file_finder_options(**options)
    tmp_dir = self._make_temp_content(items)
    f = bf_file_finder(options = finder_options)
    result = f.find_with_stats(tmp_dir)
    filenames = result.entries.filenames()
    sorted_filenames = sorted(filenames)
    return self._find_result(tmp_dir, result.entries, filenames, sorted_filenames, result.stats)
  
  def test_find_with_no_options(self):
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
    ], self._find(content).sorted_filenames )

  def test_find_absolute(self):
    content = [
      'file foo.txt "foo.txt\n"',
      'file subdir/bar.txt "bar.txt\n"',
      'file subdir/subberdir/baz.txt "baz.txt\n"',
      'file emptyfile.txt',
      'dir emptydir',
    ]
    rv = self._find(content, relative = False)
    expected_relative = [
      'emptyfile.txt',
      'foo.txt',
      'subdir/bar.txt',
      'subdir/subberdir/baz.txt'
    ]    
    expected = [ path.join(rv.tmp_dir, f) for f in expected_relative ]
    self.assert_filename_list_equal( expected, rv.sorted_filenames )

  def test_find_with_files_only(self):
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
    ], self._find(content, file_type = 'file').sorted_filenames )

  def test_find_with_dirs_only(self):
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
    ], self._find(content, file_type = 'dir').sorted_filenames )

  def test_find_with_match(self):
    content = [
      'file kiwi.py "kiwi.py\n"',
      'file foo.txt "foo.txt\n"',
      'file subdir/bar.txt "bar.txt\n"',
      'file subdir/subberdir/baz.txt "baz.txt\n"',
      'file subdir/subberdir/melon.py "melon.py\n"',
      'file emptyfile.txt',
      'dir emptydir',
    ]
    matcher = bf_file_matcher()
    matcher.add_matcher_fnmatch('*.py')
    self.assert_filename_list_equal( [
      'kiwi.py',
      'subdir/subberdir/melon.py',
    ], self._find(content, file_matcher = matcher).sorted_filenames )

  def test_find_with_max_depth(self):
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
    ]), self._find(content, max_depth = 1).sorted_filenames )
    self.assert_filename_list_equal( sorted([
      '1a.f',
      '1b.f',
      '1.d/2a.f',
      '1.d/2b.f',
    ]), self._find(content, max_depth = 2).sorted_filenames )
    self.assert_filename_list_equal( sorted([
      '1a.f',
      '1b.f',
      '1.d/2a.f',
      '1.d/2b.f',
      '1.d/2.d/3a.f',
      '1.d/2.d/3b.f',
    ]), self._find(content, max_depth = 3).sorted_filenames )
    self.assert_filename_list_equal( sorted([
      '1a.f',
      '1b.f',
      '1.d/2a.f',
      '1.d/2b.f',
      '1.d/2.d/3a.f',
      '1.d/2.d/3b.f',
      '1.d/2.d/3.d/4a.f',
      '1.d/2.d/3.d/4b.f',
    ]), self._find(content, max_depth = 4).sorted_filenames )
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
    ]), self._find(content, max_depth = 5).sorted_filenames )

  def test_find_with_min_depth(self):
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
    ]), self._find(content, min_depth = 1).sorted_filenames )
    self.assert_filename_list_equal( sorted([
      '1.d/2a.f',
      '1.d/2b.f',
      '1.d/2.d/3a.f',
      '1.d/2.d/3b.f',
      '1.d/2.d/3.d/4a.f',
      '1.d/2.d/3.d/4b.f',
      '1.d/2.d/3.d/4.d/5a.f',
      '1.d/2.d/3.d/4.d/5b.f',
    ]), self._find(content, min_depth = 2).sorted_filenames )
    self.assert_filename_list_equal( sorted([
      '1.d/2.d/3a.f',
      '1.d/2.d/3b.f',
      '1.d/2.d/3.d/4a.f',
      '1.d/2.d/3.d/4b.f',
      '1.d/2.d/3.d/4.d/5a.f',
      '1.d/2.d/3.d/4.d/5b.f',
    ]), self._find(content, min_depth = 3).sorted_filenames )
    self.assert_filename_list_equal( sorted([
      '1.d/2.d/3.d/4a.f',
      '1.d/2.d/3.d/4b.f',
      '1.d/2.d/3.d/4.d/5a.f',
      '1.d/2.d/3.d/4.d/5b.f',
    ]), self._find(content, min_depth = 4).sorted_filenames )
    self.assert_filename_list_equal( sorted([
      '1.d/2.d/3.d/4.d/5a.f',
      '1.d/2.d/3.d/4.d/5b.f',
    ]), self._find(content, min_depth = 5).sorted_filenames )
    self.assert_filename_list_equal( sorted([]), self._find(content, min_depth = 6).sorted_filenames )

  def test_find_with_min_and_max_depth(self):
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
    ]), self._find(content, min_depth = 1, max_depth = 2).sorted_filenames )
    self.assert_filename_list_equal( sorted([
      '1.d/2a.f',
      '1.d/2b.f',
      '1.d/2.d/3a.f',
      '1.d/2.d/3b.f',
    ]), self._find(content, min_depth = 2, max_depth = 3).sorted_filenames )
    self.assert_filename_list_equal( sorted([
      '1.d/2a.f',
      '1.d/2b.f',
    ]), self._find(content, min_depth = 2, max_depth = 2).sorted_filenames )
    self.assert_filename_list_equal( sorted([
      '1a.f',
      '1b.f',
    ]), self._find(content, min_depth = 1, max_depth = 1).sorted_filenames )

  def test_file_find_with_pattern(self):
    self.maxDiff = None
    content = [
      'file fruit/kiwi.fruit',
      'file fruit/lemon.fruit',
      'file fruit/strawberry.fruit',
      'file fruit/blueberry.fruit',
      'file cheese/brie.cheese',
      'file cheese/cheddar.cheese',
    ]
    matcher = bf_file_matcher()
    matcher.add_matcher_fnmatch('*.cheese')
    self.assert_filename_list_equal( [
      'cheese/brie.cheese',
      'cheese/cheddar.cheese',
    ], self._find(content, file_matcher = matcher).sorted_filenames )
    
  def test_file_find_with_pattern_and_match_type(self):
    self.maxDiff = None
    content = [
      'file fruit/kiwi.fruit',
      'file fruit/lemon.fruit',
      'file fruit/strawberry.fruit',
      'file fruit/blueberry.fruit',
      'file cheese/brie.cheese',
      'file cheese/cheddar.cheese',
    ]
    matcher = bf_file_matcher()
    matcher.add_matcher_fnmatch('*.cheese')
    self.assert_filename_list_equal( [
      'fruit/blueberry.fruit',
      'fruit/kiwi.fruit',
      'fruit/lemon.fruit',
      'fruit/strawberry.fruit',
    ], self._find(content, file_matcher = matcher, match_type = 'none').sorted_filenames )

  def test_file_find_with_path_type_basename(self):
    self.maxDiff = None
    content = [
      'file fruit/kiwi.fruit',
      'file fruit/lemon.fruit',
      'file fruit/strawberry.fruit',
      'file fruit/blueberry.fruit',
      'file cheese/brie.cheese',
      'file cheese/cheddar.cheese',
      'file bonus/fig.fruit',
    ]
    matcher = bf_file_matcher()
    matcher.add_matcher_fnmatch('f*')
    self.assert_filename_list_equal( [
      'bonus/fig.fruit',
    ], self._find(content, file_matcher = matcher, path_type = 'basename').sorted_filenames )
    
  def test_file_find_without_path_type_absolute(self):
    self.maxDiff = None
    content = [
      'file fruit/kiwi.fruit',
      'file fruit/lemon.fruit',
      'file fruit/strawberry.fruit',
      'file fruit/blueberry.fruit',
      'file cheese/brie.cheese',
      'file cheese/cheddar.cheese',
      'file bonus/fig.fruit',
    ]
    matcher = bf_file_matcher()
    matcher.add_matcher_fnmatch(self.native_filename('*fruit/kiwi.fruit'))
    self.assert_filename_list_equal( [
      'fruit/kiwi.fruit',
    ], self._find(content, file_matcher = matcher, path_type = 'absolute').sorted_filenames )

  def test_file_find_with_callable(self):
    self.maxDiff = None
    content = [
      'file fruit/kiwi.fruit',
      'file fruit/lemon.fruit',
      'file fruit/strawberry.fruit',
      'file fruit/blueberry.fruit',
      'file cheese/brie.cheese',
      'file cheese/cheddar.cheese',
    ]
    matcher = bf_file_matcher()
    matcher.add_matcher_callable(lambda f_: f_.endswith('.cheese'))
    self.assert_filename_list_equal( [
      'cheese/brie.cheese',
      'cheese/cheddar.cheese',
    ], self._find(content, file_matcher = matcher).sorted_filenames )
    
  def test_file_find_with_callable_and_match_type_any(self):
    self.maxDiff = None
    content = [
      'file fruit/kiwi.fruit',
      'file fruit/lemon.fruit',
      'file fruit/strawberry.fruit',
      'file fruit/blueberry.fruit',
      'file cheese/brie.cheese',
      'file cheese/cheddar.cheese',
    ]
    matcher = bf_file_matcher()
    matcher.add_matcher_callable(lambda f_: f_.endswith('.cheese'))
    self.assert_filename_list_equal( [
      'cheese/brie.cheese',
      'cheese/cheddar.cheese',
    ], self._find(content, file_matcher = matcher, match_type = 'any').sorted_filenames )

  def test_file_find_with_callable_and_match_type_none(self):
    self.maxDiff = None
    content = [
      'file fruit/kiwi.fruit',
      'file fruit/lemon.fruit',
      'file fruit/strawberry.fruit',
      'file fruit/blueberry.fruit',
      'file cheese/brie.cheese',
      'file cheese/cheddar.cheese',
    ]
    matcher = bf_file_matcher()
    matcher.add_matcher_callable(lambda f_: f_.endswith('.cheese'))
    self.assert_filename_list_equal( [
      'fruit/blueberry.fruit',
      'fruit/kiwi.fruit',
      'fruit/lemon.fruit',
      'fruit/strawberry.fruit',
    ], self._find(content, file_matcher = matcher, match_type = 'none').sorted_filenames )
    
  def test_file_find_with_callable_and_path_type_basename(self):
    self.maxDiff = None
    content = [
      'file fruit/kiwi.fruit',
      'file fruit/lemon.fruit',
      'file fruit/strawberry.fruit',
      'file fruit/blueberry.fruit',
      'file cheese/brie.cheese',
      'file cheese/cheddar.cheese',
    ]
    matcher = bf_file_matcher()
    matcher.add_matcher_callable(lambda f_: f_.startswith('brie'))
    self.assert_filename_list_equal( [
      'cheese/brie.cheese',
    ], self._find(content, file_matcher = matcher, path_type = 'basename').sorted_filenames )

  def test_file_find_with_callable_and_path_type_relative(self):
    self.maxDiff = None
    content = [
      'file fruit/kiwi.fruit',
      'file fruit/lemon.fruit',
      'file fruit/strawberry.fruit',
      'file fruit/blueberry.fruit',
      'file cheese/brie.cheese',
      'file cheese/cheddar.cheese',
    ]
    matcher = bf_file_matcher()
    matcher.add_matcher_callable(lambda f_: f_.startswith('cheese'))
    self.assert_filename_list_equal( [
      'cheese/brie.cheese',
      'cheese/cheddar.cheese',
    ], self._find(content, file_matcher = matcher, path_type = 'relative').sorted_filenames )

  def test_file_find_with_re(self):
    self.maxDiff = None
    content = [
      'file fruit/kiwi.fruit',
      'file fruit/lemon.fruit',
      'file fruit/strawberry.fruit',
      'file fruit/blueberry.fruit',
      'file cheese/brie.cheese',
      'file cheese/cheddar.cheese',
    ]
    matcher = bf_file_matcher()
    matcher.add_matcher_re(r'^.*\.cheese$')
    self.assert_filename_list_equal( [
      'cheese/brie.cheese',
      'cheese/cheddar.cheese',
    ], self._find(content, file_matcher = matcher).sorted_filenames )

  def test_file_find_with_re_any(self):
    self.maxDiff = None
    content = [
      'file fruit/kiwi.fruit',
      'file fruit/lemon.fruit',
      'file fruit/strawberry.fruit',
      'file fruit/blueberry.fruit',
      'file cheese/brie.cheese',
      'file cheese/cheddar.cheese',
      'file wine/barolo.wine',
      'file wine/chablis.wine',
    ]
    matcher = bf_file_matcher()
    matcher.add_matcher_re(r'^.*\.cheese$')
    matcher.add_matcher_re(r'^.*\.wine$')
    self.assert_filename_list_equal( [
      'cheese/brie.cheese',
      'cheese/cheddar.cheese',
      'wine/barolo.wine',
      'wine/chablis.wine',
    ], self._find(content, file_matcher = matcher).sorted_filenames )
    
  def test_file_find_with_re_and_match_type_none(self):
    self.maxDiff = None
    content = [
      'file fruit/kiwi.fruit',
      'file fruit/lemon.fruit',
      'file fruit/strawberry.fruit',
      'file fruit/blueberry.fruit',
      'file cheese/brie.cheese',
      'file cheese/cheddar.cheese',
    ]
    matcher = bf_file_matcher()
    matcher.add_matcher_re(r'^.*\.cheese$')
    self.assert_filename_list_equal( [
      'fruit/blueberry.fruit',
      'fruit/kiwi.fruit',
      'fruit/lemon.fruit',
      'fruit/strawberry.fruit',
    ], self._find(content, file_matcher = matcher, match_type = 'none').sorted_filenames )
    
  def test_file_find_with_re_and_basename(self):
    self.maxDiff = None
    content = [
      'file fruit/kiwi.fruit',
      'file fruit/lemon.fruit',
      'file fruit/strawberry.fruit',
      'file fruit/blueberry.fruit',
      'file cheese/brie.cheese',
      'file cheese/cheddar.cheese',
    ]
    matcher = bf_file_matcher()
    matcher.add_matcher_re(r'^f.*$')
    self.assert_filename_list_equal( [
      'fruit/blueberry.fruit',
      'fruit/kiwi.fruit',
      'fruit/lemon.fruit',
      'fruit/strawberry.fruit',
    ], self._find(content, file_matcher = matcher, path_type = 'relative').sorted_filenames )
    self.assert_filename_list_equal( [
    ], self._find(content, file_matcher = matcher, path_type = 'absolute').sorted_filenames )

  def test_find_with_match_and_negate(self):
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
    matcher = bf_file_matcher()
    matcher.add_matcher_fnmatch('.git*', negate = True)
    matcher.add_matcher_fnmatch('*.git', negate = True)
    self.assert_filename_list_equal( [
      'a/b/c/foo.txt',
      'd/e/bar.txt',
    ], self._find(content, file_matcher = matcher, match_type = 'all', path_type = 'relative').sorted_filenames )

  def test_find_with_broken_symlink(self):
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
    ], self._find(content).sorted_filenames )

  def test_find_with_broken_symlink_without_ignore_broken_links(self):
    content = [
      'file fruit/kiwi.fruit',
      'file fruit/lemon.fruit',
      'file fruit/strawberry.fruit',
      'file fruit/blueberry.fruit',
      'file cheese/brie.cheese',
      'link cheese/cheddar.cheese "/foo/notthere"',
    ]
    with self.assertRaises(OSError) as context:
      self._find(content, ignore_broken_links = False)
      self.assertTrue( 'broken symlink' in content.exception.message.lower() ) 

  def test_find_with_stop_after(self):
    content = [
      'file a/kiwi.txt',
      'file b/kiwi.txt',
      'file c/kiwi.txt',
    ]
    self.assert_filename_list_equal( [
      'a/kiwi.txt',
    ], self._find(content, stop_after = 1).sorted_filenames )

  def test_find_with_found_callback(self):
    content = [
      'file a/kiwi.txt',
      'file b/kiwi.txt',
      'file c/kiwi.txt',
    ]
    found = set()
    def _cb(entry):
      found.add(entry.filename)
    expected = [
      'a/kiwi.txt',
      'b/kiwi.txt',
      'c/kiwi.txt',
    ]
    self.assert_filename_list_equal(expected,
                                    self._find(content, found_callback = _cb).sorted_filenames )
    self.assertEqual( set(expected), found )

  def test_find_with_multiple_dirs(self):
    content = [
      'file a/kiwi.txt',
      'file b/kiwi.txt',
      'file c/kiwi.txt',
    ]
    found = set()
    def _cb(entry):
      found.add(entry.filename)
    expected = [
      'a/kiwi.txt',
      'b/kiwi.txt',
      'c/kiwi.txt',
    ]
    self.assert_filename_list_equal(expected,
                                    self._find(content, found_callback = _cb).sorted_filenames )
    self.assertEqual( set(expected), found )

  def test_find_with_multiple_dirs2(self):
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
    f = bf_file_finder()
    entries = f.find([
      path.join(tmp_dir, '1'),
      path.join(tmp_dir, '2'),
      path.join(tmp_dir, '3'),
    ])
    actual = sorted(entries.filenames())
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

  def test_find_with_match_include_and_exclude_patterns(self):
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
    matcher = bf_file_matcher()
    matcher.add_matcher_fnmatch('.git*', negate = True)
    matcher.add_matcher_fnmatch('*.git', negate = True)
    self.assert_filename_list_equal( [
      'a/b/c/foo.txt',
      'd/e/bar.txt',
    ], self._find(content, file_matcher = matcher, match_type = 'all', path_type = 'relative').sorted_filenames )
    
  def xtest_match_with_both_included_and_excluded_patterns(self):
    self.assertEqual( True, self._match_ie([ '*.py' ], [ '.*git*' ], 'src/kiwi.py', 'proj') )
    self.assertEqual( False, self._match_ie([ '*.py' ], [ '.*git*' ], '.git/cache', 'proj') )
    self.assertEqual( True, self._match_ie([ '*.py' ], [ '.*git*' ], 'src/kiwi/.git/foo', 'proj') )

  def test_find_with_stats(self):
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
    matcher = bf_file_matcher()
    matcher.add_matcher_fnmatch('.git*', negate = True)
    matcher.add_matcher_fnmatch('*.git', negate = True)
    self.assert_filename_list_equal( [
      'a/b/c/foo.txt',
      'd/e/bar.txt',
    ], self._find_with_stats(content, file_matcher = matcher, match_type = 'all', path_type = 'relative').sorted_filenames )
    
if __name__ == '__main__':
  unit_test.main()

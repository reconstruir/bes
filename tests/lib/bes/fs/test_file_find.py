#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from bes.fs.file_find import file_find
from bes.fs.temp_file import temp_file
from bes.fs.testing.temp_content import temp_content

class test_file_find(unit_test):

  @classmethod
  def _make_temp_content(clazz, items):
    return temp_content.write_items_to_temp_dir(items, delete = not clazz.DEBUG)

  def test_file_find(self):
    tmp_dir = self._make_temp_content([
      'file foo.txt "foo.txt\n"',
      'file subdir/bar.txt "bar.txt\n"',
      'file subdir/subberdir/baz.txt "baz.txt\n"',
      'file emptyfile.txt',
      'dir emptydir',
    ])

    expected_relative = [
      self.native_filename('emptyfile.txt'),
      self.native_filename('foo.txt'),
      self.native_filename('subdir/bar.txt'),
      self.native_filename('subdir/subberdir/baz.txt'),
    ]

    self.assertEqual( expected_relative, file_find.find(tmp_dir, relative = True) )

  def test_file_find_absolute(self):
    tmp_dir = self._make_temp_content([
      'file foo.txt "foo.txt\n"',
      'file subdir/bar.txt "bar.txt\n"',
      'file subdir/subberdir/baz.txt "baz.txt\n"',
      'file emptyfile.txt',
      'dir emptydir',
    ])

    expected_relative = [
      self.native_filename('emptyfile.txt'),
      self.native_filename('foo.txt'),
      self.native_filename('subdir/bar.txt'),
      self.native_filename('subdir/subberdir/baz.txt'),
    ]
    expected_absolute = [ path.join(tmp_dir, f) for f in expected_relative ]

    self.assertEqual( expected_absolute, file_find.find(tmp_dir, relative = False) )

  def test_file_find_max_depth(self):
    self.maxDiff = None
    tmp_dir = self._make_temp_content([
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
    ])

#    self.assertEqual( sorted([ '1a.f', '1b.f' ]), file_find.find(tmp_dir, max_depth = 0) )
    self.assertEqual( sorted([
      self.native_filename('1a.f'),
      self.native_filename('1b.f'),
    ]), file_find.find(tmp_dir, max_depth = 1) )
    self.assertEqual( sorted([
      self.native_filename('1a.f'),
      self.native_filename('1b.f'),
      self.native_filename('1.d/2a.f'),
      self.native_filename('1.d/2b.f'),
    ]), file_find.find(tmp_dir, max_depth = 2) )
    self.assertEqual( sorted([
      self.native_filename('1a.f'),
      self.native_filename('1b.f'),
      self.native_filename('1.d/2a.f'),
      self.native_filename('1.d/2b.f'),
      self.native_filename('1.d/2.d/3a.f'),
      self.native_filename('1.d/2.d/3b.f'),
    ]), file_find.find(tmp_dir, max_depth = 3) )
    self.assertEqual( sorted([
      self.native_filename('1a.f'),
      self.native_filename('1b.f'),
      self.native_filename('1.d/2a.f'),
      self.native_filename('1.d/2b.f'),
      self.native_filename('1.d/2.d/3a.f'),
      self.native_filename('1.d/2.d/3b.f'),
      self.native_filename('1.d/2.d/3.d/4a.f'),
      self.native_filename('1.d/2.d/3.d/4b.f'),
    ]), file_find.find(tmp_dir, max_depth = 4) )
    self.assertEqual( sorted([
      self.native_filename('1a.f'),
      self.native_filename('1b.f'),
      self.native_filename('1.d/2a.f'),
      self.native_filename('1.d/2b.f'),
      self.native_filename('1.d/2.d/3a.f'),
      self.native_filename('1.d/2.d/3b.f'),
      self.native_filename('1.d/2.d/3.d/4a.f'),
      self.native_filename('1.d/2.d/3.d/4b.f'),
      self.native_filename('1.d/2.d/3.d/4.d/5a.f'),
      self.native_filename('1.d/2.d/3.d/4.d/5b.f'),
    ]), file_find.find(tmp_dir, max_depth = 5) )

  def test_file_find_min_depth(self):
    self.maxDiff = None
    tmp_dir = self._make_temp_content([
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
    ])

    self.assertEqual( sorted([
      self.native_filename('1a.f'),
      self.native_filename('1b.f'),
      self.native_filename('1.d/2a.f'),
      self.native_filename('1.d/2b.f'),
      self.native_filename('1.d/2.d/3a.f'),
      self.native_filename('1.d/2.d/3b.f'),
      self.native_filename('1.d/2.d/3.d/4a.f'),
      self.native_filename('1.d/2.d/3.d/4b.f'),
      self.native_filename('1.d/2.d/3.d/4.d/5a.f'),
      self.native_filename('1.d/2.d/3.d/4.d/5b.f'),
    ]), file_find.find(tmp_dir, min_depth = 1) )
    self.assertEqual( sorted([
      self.native_filename('1.d/2a.f'),
      self.native_filename('1.d/2b.f'),
      self.native_filename('1.d/2.d/3a.f'),
      self.native_filename('1.d/2.d/3b.f'),
      self.native_filename('1.d/2.d/3.d/4a.f'),
      self.native_filename('1.d/2.d/3.d/4b.f'),
      self.native_filename('1.d/2.d/3.d/4.d/5a.f'),
      self.native_filename('1.d/2.d/3.d/4.d/5b.f'),
    ]), file_find.find(tmp_dir, min_depth = 2) )
    self.assertEqual( sorted([
      self.native_filename('1.d/2.d/3a.f'),
      self.native_filename('1.d/2.d/3b.f'),
      self.native_filename('1.d/2.d/3.d/4a.f'),
      self.native_filename('1.d/2.d/3.d/4b.f'),
      self.native_filename('1.d/2.d/3.d/4.d/5a.f'),
      self.native_filename('1.d/2.d/3.d/4.d/5b.f'),
    ]), file_find.find(tmp_dir, min_depth = 3) )
    self.assertEqual( sorted([
      self.native_filename('1.d/2.d/3.d/4a.f'),
      self.native_filename('1.d/2.d/3.d/4b.f'),
      self.native_filename('1.d/2.d/3.d/4.d/5a.f'),
      self.native_filename('1.d/2.d/3.d/4.d/5b.f'),
    ]), file_find.find(tmp_dir, min_depth = 4) )
    self.assertEqual( sorted([
      self.native_filename('1.d/2.d/3.d/4.d/5a.f'),
      self.native_filename('1.d/2.d/3.d/4.d/5b.f'),
    ]), file_find.find(tmp_dir, min_depth = 5) )
    self.assertEqual( sorted([]), file_find.find(tmp_dir, min_depth = 6) )

  def test_file_find_min_and_max_depth(self):
    self.maxDiff = None
    tmp_dir = self._make_temp_content([
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
    ])

    self.assertEqual( sorted([
      self.native_filename('1a.f'),
      self.native_filename('1b.f'),
      self.native_filename('1.d/2a.f'),
      self.native_filename('1.d/2b.f'),
    ]), file_find.find(tmp_dir, min_depth = 1, max_depth = 2) )
    self.assertEqual( sorted([
      self.native_filename('1.d/2a.f'),
      self.native_filename('1.d/2b.f'),
      self.native_filename('1.d/2.d/3a.f'),
      self.native_filename('1.d/2.d/3b.f'),
    ]), file_find.find(tmp_dir, min_depth = 2, max_depth = 3) )
    self.assertEqual( sorted([
      self.native_filename('1.d/2a.f'),
      self.native_filename('1.d/2b.f'),
    ]), file_find.find(tmp_dir, min_depth = 2, max_depth = 2) )
    self.assertEqual( sorted([
      self.native_filename('1a.f'),
      self.native_filename('1b.f'),
    ]), file_find.find(tmp_dir, min_depth = 1, max_depth = 1) )

  def test_file_find_with_patterns(self):
    self.maxDiff = None
    tmp_dir = self._make_temp_content([
      'file fruit/kiwi.fruit',
      'file fruit/lemon.fruit',
      'file fruit/strawberry.fruit',
      'file fruit/blueberry.fruit',
      'file cheese/brie.cheese',
      'file cheese/cheddar.cheese',
    ])
    self.assertEqual( self.native_filename_list([
      'cheese/brie.cheese',
      'cheese/cheddar.cheese',
    ]), file_find.find(tmp_dir, match_patterns = [ '*.cheese' ]) )
    
  def test_file_find_with_patterns_and_match_type(self):
    self.maxDiff = None
    tmp_dir = self._make_temp_content([
      'file fruit/kiwi.fruit',
      'file fruit/lemon.fruit',
      'file fruit/strawberry.fruit',
      'file fruit/blueberry.fruit',
      'file cheese/brie.cheese',
      'file cheese/cheddar.cheese',
    ])
    self.assertEqual( self.native_filename_list([
      'fruit/blueberry.fruit',
      'fruit/kiwi.fruit',
      'fruit/lemon.fruit',
      'fruit/strawberry.fruit',
    ]), file_find.find(tmp_dir, match_patterns = [ '*.cheese' ], match_type = 'NONE') )
    
  def test_file_find_with_patterns_and_basename(self):
    self.maxDiff = None
    tmp_dir = self._make_temp_content([
      'file fruit/kiwi.fruit',
      'file fruit/lemon.fruit',
      'file fruit/strawberry.fruit',
      'file fruit/blueberry.fruit',
      'file cheese/brie.cheese',
      'file cheese/cheddar.cheese',
    ])
    self.assertEqual( [
    ], file_find.find(tmp_dir, match_patterns = [ 'f*' ], match_basename = False) )

    self.assertEqual( self.native_filename_list([
      'fruit/blueberry.fruit',
      'fruit/kiwi.fruit',
      'fruit/lemon.fruit',
      'fruit/strawberry.fruit',
    ]), file_find.find(tmp_dir, match_patterns = [ 'f*' ], match_basename = True) )

  def test_file_find_with_function(self):
    self.maxDiff = None
    tmp_dir = self._make_temp_content([
      'file fruit/kiwi.fruit',
      'file fruit/lemon.fruit',
      'file fruit/strawberry.fruit',
      'file fruit/blueberry.fruit',
      'file cheese/brie.cheese',
      'file cheese/cheddar.cheese',
    ])
    self.assertEqual( self.native_filename_list([
      'cheese/brie.cheese',
      'cheese/cheddar.cheese',
    ]), file_find.find(tmp_dir, match_function = lambda f: f.endswith('.cheese')) )
    
  def test_file_find_with_function_and_match_type(self):
    self.maxDiff = None
    tmp_dir = self._make_temp_content([
      'file fruit/kiwi.fruit',
      'file fruit/lemon.fruit',
      'file fruit/strawberry.fruit',
      'file fruit/blueberry.fruit',
      'file cheese/brie.cheese',
      'file cheese/cheddar.cheese',
    ])
    self.assertEqual( self.native_filename_list([
      'cheese/brie.cheese',
      'cheese/cheddar.cheese',
    ]), file_find.find(tmp_dir, match_function = lambda f: f.endswith('.cheese'), match_type = 'ANY') )
    self.assertEqual( self.native_filename_list([
      'fruit/blueberry.fruit',
      'fruit/kiwi.fruit',
      'fruit/lemon.fruit',
      'fruit/strawberry.fruit',
    ]), file_find.find(tmp_dir, match_function = lambda f: f.endswith('.cheese'), match_type = 'NONE') )

  def test_file_find_with_function_and_basename(self):
    self.maxDiff = None
    tmp_dir = self._make_temp_content([
      'file fruit/kiwi.fruit',
      'file fruit/lemon.fruit',
      'file fruit/strawberry.fruit',
      'file fruit/blueberry.fruit',
      'file cheese/brie.cheese',
      'file cheese/cheddar.cheese',
    ])
    self.assertEqual( [
    ], file_find.find(tmp_dir, match_function = lambda f: f.startswith('cheese'), match_basename = False) )
    
    self.assertEqual( self.native_filename_list([
      'cheese/brie.cheese',
      'cheese/cheddar.cheese',
    ]), file_find.find(tmp_dir, match_function = lambda f: f.startswith('cheese'), match_basename = True) )

  def test_file_find_with_re(self):
    self.maxDiff = None
    tmp_dir = self._make_temp_content([
      'file fruit/kiwi.fruit',
      'file fruit/lemon.fruit',
      'file fruit/strawberry.fruit',
      'file fruit/blueberry.fruit',
      'file cheese/brie.cheese',
      'file cheese/cheddar.cheese',
    ])
    self.assertEqual( self.native_filename_list([
      'cheese/brie.cheese',
      'cheese/cheddar.cheese',
    ]), file_find.find(tmp_dir, match_re = r'^.*\.cheese$') )

  def test_file_find_with_re_list(self):
    self.maxDiff = None
    tmp_dir = self._make_temp_content([
      'file fruit/kiwi.fruit',
      'file fruit/lemon.fruit',
      'file fruit/strawberry.fruit',
      'file fruit/blueberry.fruit',
      'file cheese/brie.cheese',
      'file cheese/cheddar.cheese',
      'file wine/barolo.wine',
      'file wine/chablis.wine',
    ])
    self.assertEqual( self.native_filename_list([
      'cheese/brie.cheese',
      'cheese/cheddar.cheese',
      'wine/barolo.wine',
      'wine/chablis.wine',
    ]), file_find.find(tmp_dir, match_re = [ r'^.*\.cheese$',  r'^.*\.wine$' ]) )
    
  def test_file_find_with_re_and_match_type(self):
    self.maxDiff = None
    tmp_dir = self._make_temp_content([
      'file fruit/kiwi.fruit',
      'file fruit/lemon.fruit',
      'file fruit/strawberry.fruit',
      'file fruit/blueberry.fruit',
      'file cheese/brie.cheese',
      'file cheese/cheddar.cheese',
    ])
    self.assertEqual( self.native_filename_list([
      'fruit/blueberry.fruit',
      'fruit/kiwi.fruit',
      'fruit/lemon.fruit',
      'fruit/strawberry.fruit',
    ]), file_find.find(tmp_dir, match_re = [ r'^.*\.cheese$' ], match_type = 'NONE') )
    
  def test_file_find_with_re_and_basename(self):
    self.maxDiff = None
    tmp_dir = self._make_temp_content([
      'file fruit/kiwi.fruit',
      'file fruit/lemon.fruit',
      'file fruit/strawberry.fruit',
      'file fruit/blueberry.fruit',
      'file cheese/brie.cheese',
      'file cheese/cheddar.cheese',
    ])
    self.assertEqual( [
    ], file_find.find(tmp_dir, match_re = [ r'^f.*$' ], match_basename = False) )

    self.assertEqual( self.native_filename_list([
      'fruit/blueberry.fruit',
      'fruit/kiwi.fruit',
      'fruit/lemon.fruit',
      'fruit/strawberry.fruit',
    ]), file_find.find(tmp_dir, match_re = [ r'^f.*$' ], match_basename = True) )
    
if __name__ == '__main__':
  unit_test.main()

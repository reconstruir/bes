#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, os.path as path, unittest

from bes.testing.unit_test import unit_test

from bes.fs.file_path import file_path
from bes.fs.file_util import file_util
from bes.fs.testing.temp_content import temp_content
from bes.system.env_override import env_override

class test_file_path(unit_test):

  def test_split(self):
    self.assertEqual( [ '', 'foo', 'bar' ], file_path.split('/foo/bar') )
    self.assertEqual( [ '', 'foo', 'bar' ], file_path.split('/foo/bar/') )
    self.assertEqual( [ '', 'foo', 'bar' ], file_path.split('/foo/bar//') )
    self.assertEqual( [ 'foo', 'bar' ], file_path.split('foo/bar') )

#    assert_filename_equal
  def test_join(self):
    self.assert_filename_equal( '/foo/bar', file_path.join([ '', 'foo', 'bar' ]) )
    self.assert_filename_equal( '/foo/bar', file_path.join([ '', 'foo', 'bar' ]) )
    self.assert_filename_equal( 'foo/bar', file_path.join([ 'foo', 'bar' ]) )

  def test_replace(self):
    self.assert_filename_equal( '/foo/apple', file_path.replace('/foo/bar', 'bar', 'apple') )
    self.assert_filename_equal( '/apple/apple', file_path.replace('/bar/bar', 'bar', 'apple') )
    self.assert_filename_equal( '/apple/bar', file_path.replace('/bar/bar', 'bar', 'apple', count = 1) )
    self.assert_filename_equal( '/bar/apple', file_path.replace('/bar/bar', 'bar', 'apple', count = 1, backwards = True) )

  def test_depth(self):
    self.assertEqual( 3, file_path.depth('/foo/bar') )
    self.assertEqual( 2, file_path.depth('/foo/') )
    self.assertEqual( 1, file_path.depth('/') )
    self.assertEqual( 0, file_path.depth('') )
    
#####  def test_parent_dir(self):
#####    self.assert_filename_equal( '/foo', file_path.parent_dir('/foo/bar/') )
#####    self.assert_filename_equal( '/', file_path.parent_dir('/foo/bar') )
#####    self.assert_filename_equal( '/', file_path.parent_dir('/foo/') )
#####    self.assert_filename_equal( None, file_path.parent_dir('/foo') )
#####    self.assert_filename_equal( None, file_path.parent_dir('/') )
#####
#####  def test_parent_dir_two_levels(self):
#####    self.assert_filename_equal( None, file_path.parent_dir('/foo/bar/baz', levels = 2) )
#####    self.assert_filename_equal( None, file_path.parent_dir('/foo/bar/baz', levels = 2) )
#####    self.assert_filename_equal( None, file_path.parent_dir('/foo/bar/', levels = 2) )
#####    self.assert_filename_equal( None, file_path.parent_dir('/foo/bar', levels = 2) )
#####    self.assert_filename_equal( None, file_path.parent_dir('/foo', levels = 2) )
#####    self.assert_filename_equal( None, file_path.parent_dir('/', levels = 2) )
    
  def test_common_ancestor(self):
    self.assertEqual( 'base-1.2.3', file_path.common_ancestor([
      'base-1.2.3/foo.txt',
      'base-1.2.3/bar.txt',
      'base-1.2.3/baz.txt',
    ]) )
    self.assertEqual( 'base-1.2.3', file_path.common_ancestor([
      'base-1.2.3/foo.txt',
      'base-1.2.3/bar.txt',
      'base-1.2.3/here/baz.txt',
    ]) )
    self.assertEqual( 'base-1.2.3', file_path.common_ancestor([
      'base-1.2.3/foo.txt',
      'base-1.2.3/bar.txt',
      'base-1.2.3',
    ]) )
    self.assertEqual( 'base-1.2.3', file_path.common_ancestor([
      'base-1.2.3/foo.txt',
      'base-1.2.3/bar.txt',
      'base-1.2.3/',
    ]) )
    self.assertEqual( None, file_path.common_ancestor([
      'base-1.2.3/foo.txt',
      'base-1.2.3/bar.txt',
      'base-1.2.4/baz.txt',
    ]) )

  def test_common_ancestor_multiple_ancestors(self):
    self.assert_filename_equal( 'foo/base-1.2.3', file_path.common_ancestor([
      'foo/base-1.2.3/foo.txt',
      'foo/base-1.2.3/bar.txt',
      'foo/base-1.2.3/',
    ]) )

  def test_common_ancestor_more_multiple_ancestors(self):
    self.assert_filename_equal( 'foo/bar/base-1.2.3', file_path.common_ancestor([
      'foo/bar/base-1.2.3/foo.txt',
      'foo/bar/base-1.2.3/bar.txt',
      'foo/bar/base-1.2.3/',
    ]) )

    self.assertEqual( 'foo', file_path.common_ancestor([
      'foo/bar/base-1.2.3/foo.txt',
      'foo/bar/base-1.2.3/bar.txt',
      'foo/baz/base-1.2.3/',
    ]) )
    
  def test_common_ancestor_multiple_ancestors_absolute(self):
    self.assert_filename_equal( '/foo/base-1.2.3', file_path.common_ancestor([
      '/foo/base-1.2.3/foo.txt',
      '/foo/base-1.2.3/bar.txt',
      '/foo/base-1.2.3/',
    ]) )

  def test_common_ancestor_empty_filenames(self):
    self.assertEqual( None, file_path.common_ancestor([]) )

  def test_common_ancestor_just_one_entry(self):
    self.assertEqual( 'base-1.2.3', file_path.common_ancestor([
      'base-1.2.3/foo.txt',
    ]) )

  def test_common_ancestor_just_one_deep_entry(self):
    self.assert_filename_equal( 'foo/base-1.2.3', file_path.common_ancestor([
      'foo/base-1.2.3/foo.txt',
    ]) )
    
  def test_decompose(self):
    self.assert_filename_list_equal( [ '/foo', '/foo/bar', '/foo/bar/baz' ],
                                     file_path.decompose('/foo/bar/baz') )
    self.assert_filename_list_equal( [ '/foo', '/foo/bar' ],
                                     file_path.decompose('/foo/bar') )
    self.assert_filename_list_equal( [ '/foo' ],
                                     file_path.decompose('/foo') )
    self.assert_filename_list_equal( [],
                                     file_path.decompose('/') )

  def test_normalize_sep(self):
    self.assert_filename_equal( '/foo/bar', file_path.normalize_sep('/foo/bar') )
    self.assert_filename_equal( '/foo/bar', file_path.normalize_sep('/foo\\bar') )
    self.assert_filename_equal( '/foo/bar', file_path.normalize_sep('\\foo\\bar') )
    
  def test_which(self):
    'Test which()  Looks like a windows only test but works on unix as well.'
    tmp_dir = self.make_temp_dir()
    bin_dir = path.join(tmp_dir, 'bin')
    content = '@echo off\n\recho kiwi\n\rexit 0\n\r'
    temp_bat = file_util.save(path.join(bin_dir, 'kiwi_tool.bat'), content = content, mode = 0o0755)
    self.assertEqual( None, file_path.which('kiwi_tool.bat') )
    with env_override.path_append(bin_dir) as env:
      expected_path = path.join(bin_dir, 'kiwi_tool.bat')
      self.assertEqual( expected_path, file_path.which('kiwi_tool.bat') )

  def test_glob(self):
    tmp_dir = temp_content.write_items_to_temp_dir([
      'file fruit/fruit.config         "fruits.config" 644',
      'file cheese/cheese.config       "cheese.config" 644',
      'file drinks/alcohol/wine.config "wine.config"   644',
      'file drinks/alcohol/beer.config "beer.config"   644',
      'file drinks/dairy/milk.config   "milk.config"   644',
      'file drinks/dairy/yogurt.config "yogurt.config" 644',
      'dir  nothing                 ""                 700',
    ])
    self.assert_filename_list_equal( [
      f'{tmp_dir}/drinks/alcohol/beer.config',
      f'{tmp_dir}/drinks/alcohol/wine.config',
    ], file_path.glob(path.join(tmp_dir, 'drinks/alcohol'), '*.config') )
    
  def test_glob_search_path(self):
    tmp_dir = temp_content.write_items_to_temp_dir([
      'file fruit/fruit.config         "fruits.config" 644',
      'file cheese/cheese.config       "cheese.config" 644',
      'file drinks/alcohol/wine.config "wine.config"   644',
      'file drinks/alcohol/beer.config "beer.config"   644',
      'file drinks/dairy/milk.config   "milk.config"   644',
      'file drinks/dairy/yogurt.config "yogurt.config" 644',
      'dir  nothing                 ""                 700',
    ])
    search_path = [
      [ 'fruit' ],
      [ 'cheese' ],
      [ 'drinks', 'alcohol' ],
      [ 'drinks', 'dairy' ],
    ]
    search_path = [ path.join(tmp_dir, *x) for x in search_path ]
    self.assert_filename_list_equal( [
      f'{tmp_dir}/cheese/cheese.config',
      f'{tmp_dir}/drinks/alcohol/beer.config',
      f'{tmp_dir}/drinks/alcohol/wine.config',
      f'{tmp_dir}/drinks/dairy/milk.config',
      f'{tmp_dir}/drinks/dairy/yogurt.config',
      f'{tmp_dir}/fruit/fruit.config',
    ], file_path.glob(search_path, '*.config') )

  def xtest_glob_env_search_path(self):
    tmp_dir = temp_content.write_items_to_temp_dir([
      'file fruit/fruit.config         "fruits.config" 644',
      'file cheese/cheese.config       "cheese.config" 644',
      'file drinks/alcohol/wine.config "wine.config"   644',
      'file drinks/alcohol/beer.config "beer.config"   644',
      'file drinks/dairy/milk.config   "milk.config"   644',
      'file drinks/dairy/yogurt.config "yogurt.config" 644',
      'dir  nothing                 ""                 700',
    ])
    search_path = [
      [ 'fruit' ],
      [ 'cheese' ],
      [ 'drinks', 'alcohol' ],
      [ 'drinks', 'dairy' ],
    ]
    search_path = [ '{}/{}'.format(tmp_dir, path.join(x)) for x in search_path ]
    self.assert_filename_list_equal( [
      f'{tmp_dir}/cheese/cheese.config',
      f'{tmp_dir}/drinks/alcohol/beer.config',
      f'{tmp_dir}/drinks/alcohol/wine.config',
      f'{tmp_dir}/drinks/dairy/milk.config',
      f'{tmp_dir}/drinks/dairy/yogurt.config',
      f'{tmp_dir}/fruit/fruit.config',
    ], file_path.glob(search_path, '*.config') )

  def test_has_glob_pattern_true(self):
    self.assertTrue( file_path.has_glob_pattern('*.py') )
    self.assertTrue( file_path.has_glob_pattern('*.??') )

  def test_has_glob_pattern_false(self):
    self.assertFalse( file_path.has_glob_pattern('foo.py') )

  def test_insert(self):
    self.assert_filename_equal( '/foo/bar/baz/x.png', file_path.insert('/foo/bar/x.png', -1, 'baz') )
    self.assert_filename_equal( '/baz/foo/bar/x.png', file_path.insert('/foo/bar/x.png', 1, 'baz') )

  def test_replace_all(self):
    self.assert_filename_equal( '/foo/apple', file_path.replace_all('/foo/bar', 'bar', 'apple') )
    self.assert_filename_equal( '/apple/foo/apple', file_path.replace_all('/bar/foo/bar', 'bar', 'apple') )
    
if __name__ == '__main__':
  unit_test.main()

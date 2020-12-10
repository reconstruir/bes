#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, os.path as path, unittest

from bes.testing.unit_test import unit_test

from bes.fs.file_path import file_path as FP
from bes.fs.file_util import file_util
from bes.fs.testing.temp_content import temp_content
from bes.system.env_override import env_override

class test_file_path(unit_test):

  def test_split(self):
    self.assertEqual( [ '', 'foo', 'bar' ], FP.split('/foo/bar') )
    self.assertEqual( [ '', 'foo', 'bar' ], FP.split('/foo/bar/') )
    self.assertEqual( [ '', 'foo', 'bar' ], FP.split('/foo/bar//') )
    self.assertEqual( [ 'foo', 'bar' ], FP.split('foo/bar') )

  def test_join(self):
    self.assertEqual( self.p('/foo/bar'), FP.join([ '', 'foo', 'bar' ]) )
    self.assertEqual( self.p('/foo/bar'), FP.join([ '', 'foo', 'bar' ]) )
    self.assertEqual( self.p('foo/bar'), FP.join([ 'foo', 'bar' ]) )

  def test_replace(self):
    self.assertEqual( self.p('/foo/apple'), FP.replace(self.p('/foo/bar'), 'bar', 'apple') )
    self.assertEqual( self.p('/apple/apple'), FP.replace(self.p('/bar/bar'), 'bar', 'apple') )
    self.assertEqual( self.p('/apple/bar'), FP.replace(self.p('/bar/bar'), 'bar', 'apple', count = 1) )
    self.assertEqual( self.p('/bar/apple'), FP.replace(self.p('/bar/bar'), 'bar', 'apple', count = 1, backwards = True) )

  def test_depth(self):
    self.assertEqual( 3, FP.depth('/foo/bar') )
    self.assertEqual( 2, FP.depth('/foo/') )
    self.assertEqual( 1, FP.depth('/') )
    self.assertEqual( 0, FP.depth('') )
    
  def test_parent_dir(self):
    self.assertEqual( self.p('/foo'), FP.parent_dir(self.p('/foo/bar/')) )
    self.assertEqual( self.p('/foo'), FP.parent_dir(self.p('/foo/bar')) )
    self.assertEqual( self.p('/'), FP.parent_dir(self.p('/foo')) )
    self.assertEqual( None, FP.parent_dir(self.p('/')) )

  def test_common_ancestor(self):
    self.assertEqual( 'base-1.2.3', FP.common_ancestor([
      'base-1.2.3/foo.txt',
      'base-1.2.3/bar.txt',
      'base-1.2.3/baz.txt',
    ]) )
    self.assertEqual( 'base-1.2.3', FP.common_ancestor([
      'base-1.2.3/foo.txt',
      'base-1.2.3/bar.txt',
      'base-1.2.3/here/baz.txt',
    ]) )
    self.assertEqual( 'base-1.2.3', FP.common_ancestor([
      'base-1.2.3/foo.txt',
      'base-1.2.3/bar.txt',
      'base-1.2.3',
    ]) )
    self.assertEqual( 'base-1.2.3', FP.common_ancestor([
      'base-1.2.3/foo.txt',
      'base-1.2.3/bar.txt',
      'base-1.2.3/',
    ]) )
    self.assertEqual( None, FP.common_ancestor([
      'base-1.2.3/foo.txt',
      'base-1.2.3/bar.txt',
      'base-1.2.4/baz.txt',
    ]) )

  def test_common_ancestor_multiple_ancestors(self):
    self.assertEqual( 'foo/base-1.2.3', FP.common_ancestor([
      'foo/base-1.2.3/foo.txt',
      'foo/base-1.2.3/bar.txt',
      'foo/base-1.2.3/',
    ]) )

  def test_common_ancestor_more_multiple_ancestors(self):
    self.assertEqual( 'foo/bar/base-1.2.3', FP.common_ancestor([
      'foo/bar/base-1.2.3/foo.txt',
      'foo/bar/base-1.2.3/bar.txt',
      'foo/bar/base-1.2.3/',
    ]) )

    self.assertEqual( 'foo', FP.common_ancestor([
      'foo/bar/base-1.2.3/foo.txt',
      'foo/bar/base-1.2.3/bar.txt',
      'foo/baz/base-1.2.3/',
    ]) )
    
  def test_common_ancestor_multiple_ancestors_absolute(self):
    self.assertEqual( '/foo/base-1.2.3', FP.common_ancestor([
      '/foo/base-1.2.3/foo.txt',
      '/foo/base-1.2.3/bar.txt',
      '/foo/base-1.2.3/',
    ]) )

  def test_common_ancestor_empty_filenames(self):
    self.assertEqual( None, FP.common_ancestor([]) )

  def test_common_ancestor_just_one_entry(self):
    self.assertEqual( 'base-1.2.3', FP.common_ancestor([
      'base-1.2.3/foo.txt',
    ]) )

  def test_common_ancestor_just_one_deep_entry(self):
    self.assertEqual( 'foo/base-1.2.3', FP.common_ancestor([
      'foo/base-1.2.3/foo.txt',
    ]) )
    
  def test_decompose(self):
    self.assertEqual( [ self.p('/foo'), self.p('/foo/bar'), self.p('/foo/bar/baz') ], FP.decompose(self.p('/foo/bar/baz')) )
    self.assertEqual( [ self.p('/foo'), self.p('/foo/bar') ], FP.decompose(self.p('/foo/bar')) )
    self.assertEqual( [ self.p('/foo'), ], FP.decompose(self.p('/foo')) )
    self.assertEqual( [], FP.decompose(self.p('/')) )

  def test_normalize_sep(self):
    self.assertEqual( self.p('/foo/bar'), FP.normalize_sep('/foo/bar') )
    self.assertEqual( self.p('/foo/bar'), FP.normalize_sep('/foo\\bar') )
    self.assertEqual( self.p('/foo/bar'), FP.normalize_sep('\\foo\\bar') )
    
  def test_which(self):
    'Test which()  Looks like a windows only test but works on unix as well.'
    tmp_dir = self.make_temp_dir()
    bin_dir = path.join(tmp_dir, 'bin')
    content = '@echo off\n\recho kiwi\n\rexit 0\n\r'
    temp_bat = file_util.save(path.join(bin_dir, 'kiwi_tool.bat'), content = content, mode = 0o0755)
    self.assertEqual( None, FP.which('kiwi_tool.bat') )
    with env_override.path_append(bin_dir) as env:
      expected_path = path.join(bin_dir, 'kiwi_tool.bat')
      self.assertEqual( expected_path, FP.which('kiwi_tool.bat') )

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
    self.assertEqual( [
      path.join(tmp_dir, 'drinks/alcohol/beer.config'),
      path.join(tmp_dir, 'drinks/alcohol/wine.config'),
    ], FP.glob(path.join(tmp_dir, 'drinks/alcohol'), '*.config') )
    
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
    self.assertEqual( [
      path.join(tmp_dir, 'cheese/cheese.config'),
      path.join(tmp_dir, 'drinks/alcohol/beer.config'),
      path.join(tmp_dir, 'drinks/alcohol/wine.config'),
      path.join(tmp_dir, 'drinks/dairy/milk.config'),
      path.join(tmp_dir, 'drinks/dairy/yogurt.config'),
      path.join(tmp_dir, 'fruit/fruit.config'),
    ], FP.glob(search_path, '*.config') )

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
    self.assertEqual( [
      path.join(tmp_dir, 'cheese/cheese.config'),
      path.join(tmp_dir, 'drinks/alcohol/beer.config'),
      path.join(tmp_dir, 'drinks/alcohol/wine.config'),
      path.join(tmp_dir, 'drinks/dairy/milk.config'),
      path.join(tmp_dir, 'drinks/dairy/yogurt.config'),
      path.join(tmp_dir, 'fruit/fruit.config'),
    ], FP.glob(search_path, '*.config') )

  def test_has_glob_pattern_true(self):
    self.assertTrue( FP.has_glob_pattern('*.py') )
    self.assertTrue( FP.has_glob_pattern('*.??') )

  def test_has_glob_pattern_false(self):
    self.assertFalse( FP.has_glob_pattern('foo.py') )
    
if __name__ == "__main__":
  unit_test.main()

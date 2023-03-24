#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, os.path as path, unittest

from bes.testing.unit_test import unit_test

from bes.files.bf_path import bf_path
from bes.system.env_override import env_override
from bes.text.word_boundary import word_boundary

class test_bf_path(unit_test):

  def test_split(self):
    self.assertEqual( [ '', 'foo', 'bar' ], bf_path.split('/foo/bar') )
    self.assertEqual( [ '', 'foo', 'bar' ], bf_path.split('/foo/bar/') )
    self.assertEqual( [ '', 'foo', 'bar' ], bf_path.split('/foo/bar//') )
    self.assertEqual( [ 'foo', 'bar' ], bf_path.split('foo/bar') )

  def test_join(self):
    self.assert_filename_equal( '/foo/bar', bf_path.join([ '', 'foo', 'bar' ]) )
    self.assert_filename_equal( '/foo/bar', bf_path.join([ '', 'foo', 'bar' ]) )
    self.assert_filename_equal( 'foo/bar', bf_path.join([ 'foo', 'bar' ]) )

  def test_replace(self):
    self.assert_filename_equal( '/foo/apple', bf_path.replace('/foo/bar', 'bar', 'apple') )
    self.assert_filename_equal( '/apple/apple', bf_path.replace('/bar/bar', 'bar', 'apple') )
    self.assert_filename_equal( '/apple/bar', bf_path.replace('/bar/bar', 'bar', 'apple', count = 1) )
    self.assert_filename_equal( '/bar/apple', bf_path.replace('/bar/bar', 'bar', 'apple', count = 1, backwards = True) )

  def test_depth(self):
    self.assertEqual( 3, bf_path.depth('/foo/bar') )
    self.assertEqual( 2, bf_path.depth('/foo/') )
    self.assertEqual( 1, bf_path.depth('/') )
    self.assertEqual( 0, bf_path.depth('') )
    
  def test_common_ancestor(self):
    self.assertEqual( 'base-1.2.3', bf_path.common_ancestor([
      'base-1.2.3/foo.txt',
      'base-1.2.3/bar.txt',
      'base-1.2.3/baz.txt',
    ]) )
    self.assertEqual( 'base-1.2.3', bf_path.common_ancestor([
      'base-1.2.3/foo.txt',
      'base-1.2.3/bar.txt',
      'base-1.2.3/here/baz.txt',
    ]) )
    self.assertEqual( 'base-1.2.3', bf_path.common_ancestor([
      'base-1.2.3/foo.txt',
      'base-1.2.3/bar.txt',
      'base-1.2.3',
    ]) )
    self.assertEqual( 'base-1.2.3', bf_path.common_ancestor([
      'base-1.2.3/foo.txt',
      'base-1.2.3/bar.txt',
      'base-1.2.3/',
    ]) )
    self.assertEqual( None, bf_path.common_ancestor([
      'base-1.2.3/foo.txt',
      'base-1.2.3/bar.txt',
      'base-1.2.4/baz.txt',
    ]) )

  def test_common_ancestor_multiple_ancestors(self):
    self.assert_filename_equal( 'foo/base-1.2.3', bf_path.common_ancestor([
      'foo/base-1.2.3/foo.txt',
      'foo/base-1.2.3/bar.txt',
      'foo/base-1.2.3/',
    ]) )

  def test_common_ancestor_more_multiple_ancestors(self):
    self.assert_filename_equal( 'foo/bar/base-1.2.3', bf_path.common_ancestor([
      'foo/bar/base-1.2.3/foo.txt',
      'foo/bar/base-1.2.3/bar.txt',
      'foo/bar/base-1.2.3/',
    ]) )

    self.assertEqual( 'foo', bf_path.common_ancestor([
      'foo/bar/base-1.2.3/foo.txt',
      'foo/bar/base-1.2.3/bar.txt',
      'foo/baz/base-1.2.3/',
    ]) )
    
  def test_common_ancestor_multiple_ancestors_absolute(self):
    self.assert_filename_equal( '/foo/base-1.2.3', bf_path.common_ancestor([
      '/foo/base-1.2.3/foo.txt',
      '/foo/base-1.2.3/bar.txt',
      '/foo/base-1.2.3/',
    ]) )

  def test_common_ancestor_empty_filenames(self):
    self.assertEqual( None, bf_path.common_ancestor([]) )

  def test_common_ancestor_just_one_entry(self):
    self.assertEqual( 'base-1.2.3', bf_path.common_ancestor([
      'base-1.2.3/foo.txt',
    ]) )

  def test_common_ancestor_just_one_deep_entry(self):
    self.assert_filename_equal( 'foo/base-1.2.3', bf_path.common_ancestor([
      'foo/base-1.2.3/foo.txt',
    ]) )
    
  def test_decompose(self):
    self.assert_filename_list_equal( [ '/foo', '/foo/bar', '/foo/bar/baz' ],
                                     bf_path.decompose('/foo/bar/baz') )
    self.assert_filename_list_equal( [ '/foo', '/foo/bar' ],
                                     bf_path.decompose('/foo/bar') )
    self.assert_filename_list_equal( [ '/foo' ],
                                     bf_path.decompose('/foo') )
    self.assert_filename_list_equal( [],
                                     bf_path.decompose('/') )

  def test_normalize_sep(self):
    self.assert_filename_equal( '/foo/bar', bf_path.normalize_sep('/foo/bar') )
    self.assert_filename_equal( '/foo/bar', bf_path.normalize_sep('/foo\\bar') )
    self.assert_filename_equal( '/foo/bar', bf_path.normalize_sep('\\foo\\bar') )

  def test_insert(self):
    self.assert_filename_equal( '/foo/bar/baz/x.png', bf_path.insert('/foo/bar/x.png', -1, 'baz') )
    self.assert_filename_equal( '/baz/foo/bar/x.png', bf_path.insert('/foo/bar/x.png', 1, 'baz') )

  def test_replace_all(self):
    self.assert_filename_equal( '/foo/apple', bf_path.replace_all('/foo/bar', 'bar', 'apple') )
    self.assert_filename_equal( '/apple/foo/apple', bf_path.replace_all('/bar/foo/bar', 'bar', 'apple') )
    self.assert_filename_equal( '/applefruit/apple_fruit/foo', bf_path.replace_all('/kiwifruit/kiwi_fruit/foo', 'kiwi', 'apple') )

  def test_replace_all_with_word_boundary(self):
    self.assert_filename_equal( '/kiwifruit/kiwi_fruit/foo',
                                bf_path.replace_all('/kiwifruit/kiwi_fruit/foo', 'kiwi', 'apple', word_boundary = True) )
    
  def test_replace_all_with_word_boundary_and_underscore(self):
    self.assert_filename_equal( '/kiwifruit/apple_fruit/foo',
                                bf_path.replace_all('/kiwifruit/kiwi_fruit/foo',
                                                      'kiwi',
                                                      'apple',
                                                      word_boundary = True,
                                                      word_boundary_chars = word_boundary.CHARS_UNDERSCORE) )

  @classmethod
  def _test_shorten(clazz, p, max_path_length, max_filename_length):
    return bf_path.shorten(p,
                              max_path_length = max_path_length,
                              max_filename_length = max_filename_length)
  
  def test_shorten(self):
    self.assert_filename_equal( '/tmp/foo.jpg', self._test_shorten('/tmp/foo_bar.jpg', 12, 1000) )
    self.assert_filename_equal( '/tmp/fo.jpg', self._test_shorten('/tmp/foo_bar.jpg', 11, 1000) )
    self.assert_filename_equal( '/tmp/f.jpg', self._test_shorten('/tmp/foo_bar.jpg', 10, 1000) )

  def test_shorten_no_extension(self):
    self.assert_filename_equal( '/tmp/foo_bar', self._test_shorten('/tmp/foo_bar_baz', 12, 1000) )
    
  def test_shorten_not_enough_space(self):
    with self.assertRaises(ValueError) as _:
      self._test_shorten('/tmp/foo_bar.jpg', 9, 1000)
    with self.assertRaises(ValueError) as _:
      self._test_shorten('/tmp/foo_bar.jpg', 8, 1000)

if __name__ == '__main__':
  unit_test.main()

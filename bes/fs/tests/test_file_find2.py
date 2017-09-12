#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import os, os.path as path
from collections import namedtuple
from bes.testing.unit_test import unit_test
from bes.fs import file_find2, file_util, temp_file

class test_file_find2(unit_test):

  Item = namedtuple('Item', [ 'filename', 'content', 'isdir' ])

  @classmethod
  def _parse_item(clazz, item):
    if isinstance(item, basestring):
      item = ( item, None )
    assert isinstance(item, tuple)
    assert len(item) >= 1
    filename = item[0]
    isdir = False
    content = None
    if filename.endswith(os.sep):
      isdir = True
      filename = path.normpath(filename)
    if len(item) >= 2:
      content = item[1]
    return clazz.Item(filename, content, isdir)

  @classmethod
  def _make_temp_items(clazz, items):
    return [ clazz._parse_item(item) for item in items ]

  @classmethod
  def _write_temp_content(clazz, root_dir, items):
    items = clazz._make_temp_items(items)
    for item in items:
      filename = path.join(root_dir, item.filename)
      if item.isdir:
        file_util.mkdir(filename)
      else:
        file_util.save(filename, item.content)

  @classmethod
  def _make_temp_content(clazz, items):
    tmp_dir = temp_file.make_temp_dir()
    clazz._write_temp_content(tmp_dir, items)
    return tmp_dir

  def test_file_find2(self):
    tmp_dir = self._make_temp_content([
      ( 'foo.txt', 'foo.txt\n' ),
      ( 'subdir/bar.txt', 'bar.txt\n' ),
      ( 'subdir/subberdir/baz.txt', 'baz.txt\n' ),
      ( 'emptyfile.txt' ),
      ( 'emptydir/' ),
    ])

    expected_relative = [
      'emptyfile.txt',
      'foo.txt',
      'subdir/bar.txt',
      'subdir/subberdir/baz.txt',
    ]

    self.assertEqual( expected_relative, file_find2.find(tmp_dir, relative = True) )

  def test_file_find2_absolute(self):
    tmp_dir = self._make_temp_content([
      ( 'foo.txt', 'foo.txt\n' ),
      ( 'subdir/bar.txt', 'bar.txt\n' ),
      ( 'subdir/subberdir/baz.txt', 'baz.txt\n' ),
      ( 'emptyfile.txt' ),
      ( 'emptydir/' ),
    ])

    expected_relative = [
      'emptyfile.txt',
      'foo.txt',
      'subdir/bar.txt',
      'subdir/subberdir/baz.txt',
    ]
    expected_absolute = [ path.join(tmp_dir, f) for f in expected_relative ]

    self.assertEqual( expected_absolute, file_find2.find(tmp_dir, relative = False) )

  def test_file_find2_max_depth(self):
    self.maxDiff = None
    tmp_dir = self._make_temp_content([
      ( '1a.f' ),
      ( '1b.f' ),
      ( '1.d/2a.f' ),
      ( '1.d/2b.f' ),
      ( '1.d/2.d/3a.f' ),
      ( '1.d/2.d/3b.f' ),
      ( '1.d/2.d/3.d/4a.f' ),
      ( '1.d/2.d/3.d/4b.f' ),
      ( '1.d/2.d/3.d/4.d/5a.f' ),
      ( '1.d/2.d/3.d/4.d/5b.f' ),
    ])

#    self.assertEqual( sorted([ '1a.f', '1b.f' ]), file_find2.find(tmp_dir, max_depth = 0) )
    self.assertEqual( sorted([ '1a.f', '1b.f' ]), file_find2.find(tmp_dir, max_depth = 1) )
    self.assertEqual( sorted([ '1a.f', '1b.f', '1.d/2a.f', '1.d/2b.f' ]), file_find2.find(tmp_dir, max_depth = 2) )
    self.assertEqual( sorted([ '1a.f', '1b.f', '1.d/2a.f', '1.d/2b.f', '1.d/2.d/3a.f', '1.d/2.d/3b.f' ]), file_find2.find(tmp_dir, max_depth = 3) )
    self.assertEqual( sorted([ '1a.f', '1b.f', '1.d/2a.f', '1.d/2b.f', '1.d/2.d/3a.f', '1.d/2.d/3b.f', '1.d/2.d/3.d/4a.f', '1.d/2.d/3.d/4b.f' ]), file_find2.find(tmp_dir, max_depth = 4) )
    self.assertEqual( sorted([ '1a.f', '1b.f', '1.d/2a.f', '1.d/2b.f', '1.d/2.d/3a.f', '1.d/2.d/3b.f', '1.d/2.d/3.d/4a.f', '1.d/2.d/3.d/4b.f', '1.d/2.d/3.d/4.d/5a.f', '1.d/2.d/3.d/4.d/5b.f' ]), file_find2.find(tmp_dir, max_depth = 5) )

  def test_file_find2_min_depth(self):
    self.maxDiff = None
    tmp_dir = self._make_temp_content([
      ( '1a.f' ),
      ( '1b.f' ),
      ( '1.d/2a.f' ),
      ( '1.d/2b.f' ),
      ( '1.d/2.d/3a.f' ),
      ( '1.d/2.d/3b.f' ),
      ( '1.d/2.d/3.d/4a.f' ),
      ( '1.d/2.d/3.d/4b.f' ),
      ( '1.d/2.d/3.d/4.d/5a.f' ),
      ( '1.d/2.d/3.d/4.d/5b.f' ),
    ])

    self.assertEqual( sorted([ '1a.f', '1b.f', '1.d/2a.f', '1.d/2b.f', '1.d/2.d/3a.f', '1.d/2.d/3b.f', '1.d/2.d/3.d/4a.f', '1.d/2.d/3.d/4b.f', '1.d/2.d/3.d/4.d/5a.f', '1.d/2.d/3.d/4.d/5b.f' ]), file_find2.find(tmp_dir, min_depth = 1) )
    self.assertEqual( sorted([ '1.d/2a.f', '1.d/2b.f', '1.d/2.d/3a.f', '1.d/2.d/3b.f', '1.d/2.d/3.d/4a.f', '1.d/2.d/3.d/4b.f', '1.d/2.d/3.d/4.d/5a.f', '1.d/2.d/3.d/4.d/5b.f' ]), file_find2.find(tmp_dir, min_depth = 2) )
    self.assertEqual( sorted([ '1.d/2.d/3a.f', '1.d/2.d/3b.f', '1.d/2.d/3.d/4a.f', '1.d/2.d/3.d/4b.f', '1.d/2.d/3.d/4.d/5a.f', '1.d/2.d/3.d/4.d/5b.f' ]), file_find2.find(tmp_dir, min_depth = 3) )
    self.assertEqual( sorted([ '1.d/2.d/3.d/4a.f', '1.d/2.d/3.d/4b.f', '1.d/2.d/3.d/4.d/5a.f', '1.d/2.d/3.d/4.d/5b.f' ]), file_find2.find(tmp_dir, min_depth = 4) )
    self.assertEqual( sorted([ '1.d/2.d/3.d/4.d/5a.f', '1.d/2.d/3.d/4.d/5b.f' ]), file_find2.find(tmp_dir, min_depth = 5) )
    self.assertEqual( sorted([]), file_find2.find(tmp_dir, min_depth = 6) )

  def test_file_find2_min_and_max_depth(self):
    self.maxDiff = None
    tmp_dir = self._make_temp_content([
      ( '1a.f' ),
      ( '1b.f' ),
      ( '1.d/2a.f' ),
      ( '1.d/2b.f' ),
      ( '1.d/2.d/3a.f' ),
      ( '1.d/2.d/3b.f' ),
      ( '1.d/2.d/3.d/4a.f' ),
      ( '1.d/2.d/3.d/4b.f' ),
      ( '1.d/2.d/3.d/4.d/5a.f' ),
      ( '1.d/2.d/3.d/4.d/5b.f' ),
    ])

    self.assertEqual( sorted([ '1a.f', '1b.f', '1.d/2a.f', '1.d/2b.f' ]), file_find2.find(tmp_dir, min_depth = 1, max_depth = 2) )
    self.assertEqual( sorted([ '1.d/2a.f', '1.d/2b.f', '1.d/2.d/3a.f', '1.d/2.d/3b.f' ]), file_find2.find(tmp_dir, min_depth = 2, max_depth = 3) )
    self.assertEqual( sorted([ '1.d/2a.f', '1.d/2b.f' ]), file_find2.find(tmp_dir, min_depth = 2, max_depth = 2) )
    self.assertEqual( sorted([ '1a.f', '1b.f' ]), file_find2.find(tmp_dir, min_depth = 1, max_depth = 1) )

if __name__ == "__main__":
  unit_test.main()

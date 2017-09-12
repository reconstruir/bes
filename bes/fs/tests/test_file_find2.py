#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from bes.fs import file_find2, temp_file
from bes.fs.testing import temp_content

class test_file_find2(unit_test):

  @classmethod
  def _make_temp_content(clazz, items):
    tmp_dir = temp_file.make_temp_dir()
    temp_content.write_items(items, tmp_dir)
    return tmp_dir

  def test_file_find(self):
    tmp_dir = self._make_temp_content([
      'file foo.txt "foo.txt\n"',
      'file subdir/bar.txt "bar.txt\n"',
      'file subdir/subberdir/baz.txt "baz.txt\n"',
      'file emptyfile.txt',
      'dir emptydir',
    ])

    expected_relative = [
      'emptyfile.txt',
      'foo.txt',
      'subdir/bar.txt',
      'subdir/subberdir/baz.txt',
    ]

    self.assertEqual( expected_relative, file_find2.find(tmp_dir, relative = True) )

  def test_file_find_absolute(self):
    tmp_dir = self._make_temp_content([
      'file foo.txt "foo.txt\n"',
      'file subdir/bar.txt "bar.txt\n"',
      'file subdir/subberdir/baz.txt "baz.txt\n"',
      'file emptyfile.txt',
      'dir emptydir',
    ])

    expected_relative = [
      'emptyfile.txt',
      'foo.txt',
      'subdir/bar.txt',
      'subdir/subberdir/baz.txt',
    ]
    expected_absolute = [ path.join(tmp_dir, f) for f in expected_relative ]

    self.assertEqual( expected_absolute, file_find2.find(tmp_dir, relative = False) )

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

#    self.assertEqual( sorted([ '1a.f', '1b.f' ]), file_find2.find(tmp_dir, max_depth = 0) )
    self.assertEqual( sorted([ '1a.f', '1b.f' ]), file_find2.find(tmp_dir, max_depth = 1) )
    self.assertEqual( sorted([ '1a.f', '1b.f', '1.d/2a.f', '1.d/2b.f' ]), file_find2.find(tmp_dir, max_depth = 2) )
    self.assertEqual( sorted([ '1a.f', '1b.f', '1.d/2a.f', '1.d/2b.f', '1.d/2.d/3a.f', '1.d/2.d/3b.f' ]), file_find2.find(tmp_dir, max_depth = 3) )
    self.assertEqual( sorted([ '1a.f', '1b.f', '1.d/2a.f', '1.d/2b.f', '1.d/2.d/3a.f', '1.d/2.d/3b.f', '1.d/2.d/3.d/4a.f', '1.d/2.d/3.d/4b.f' ]), file_find2.find(tmp_dir, max_depth = 4) )
    self.assertEqual( sorted([ '1a.f', '1b.f', '1.d/2a.f', '1.d/2b.f', '1.d/2.d/3a.f', '1.d/2.d/3b.f', '1.d/2.d/3.d/4a.f', '1.d/2.d/3.d/4b.f', '1.d/2.d/3.d/4.d/5a.f', '1.d/2.d/3.d/4.d/5b.f' ]), file_find2.find(tmp_dir, max_depth = 5) )

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

    self.assertEqual( sorted([ '1a.f', '1b.f', '1.d/2a.f', '1.d/2b.f', '1.d/2.d/3a.f', '1.d/2.d/3b.f', '1.d/2.d/3.d/4a.f', '1.d/2.d/3.d/4b.f', '1.d/2.d/3.d/4.d/5a.f', '1.d/2.d/3.d/4.d/5b.f' ]), file_find2.find(tmp_dir, min_depth = 1) )
    self.assertEqual( sorted([ '1.d/2a.f', '1.d/2b.f', '1.d/2.d/3a.f', '1.d/2.d/3b.f', '1.d/2.d/3.d/4a.f', '1.d/2.d/3.d/4b.f', '1.d/2.d/3.d/4.d/5a.f', '1.d/2.d/3.d/4.d/5b.f' ]), file_find2.find(tmp_dir, min_depth = 2) )
    self.assertEqual( sorted([ '1.d/2.d/3a.f', '1.d/2.d/3b.f', '1.d/2.d/3.d/4a.f', '1.d/2.d/3.d/4b.f', '1.d/2.d/3.d/4.d/5a.f', '1.d/2.d/3.d/4.d/5b.f' ]), file_find2.find(tmp_dir, min_depth = 3) )
    self.assertEqual( sorted([ '1.d/2.d/3.d/4a.f', '1.d/2.d/3.d/4b.f', '1.d/2.d/3.d/4.d/5a.f', '1.d/2.d/3.d/4.d/5b.f' ]), file_find2.find(tmp_dir, min_depth = 4) )
    self.assertEqual( sorted([ '1.d/2.d/3.d/4.d/5a.f', '1.d/2.d/3.d/4.d/5b.f' ]), file_find2.find(tmp_dir, min_depth = 5) )
    self.assertEqual( sorted([]), file_find2.find(tmp_dir, min_depth = 6) )

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

    self.assertEqual( sorted([ '1a.f', '1b.f', '1.d/2a.f', '1.d/2b.f' ]), file_find2.find(tmp_dir, min_depth = 1, max_depth = 2) )
    self.assertEqual( sorted([ '1.d/2a.f', '1.d/2b.f', '1.d/2.d/3a.f', '1.d/2.d/3b.f' ]), file_find2.find(tmp_dir, min_depth = 2, max_depth = 3) )
    self.assertEqual( sorted([ '1.d/2a.f', '1.d/2b.f' ]), file_find2.find(tmp_dir, min_depth = 2, max_depth = 2) )
    self.assertEqual( sorted([ '1a.f', '1b.f' ]), file_find2.find(tmp_dir, min_depth = 1, max_depth = 1) )

if __name__ == "__main__":
  unit_test.main()

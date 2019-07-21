#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, sys
from os import path

from bes.testing.unit_test import unit_test
from bes.fs.testing.temp_content import temp_content

from bes.fs.fs.fs_local import fs_local

class test_fs_local(unit_test):

  def test_fs_local(self):
    tmp_dir = self._make_temp_content([
      'file foo.txt "foo.txt\n"',
      'file subdir/bar.txt "bar.txt\n"',
      'file subdir/subberdir/baz.txt "baz.txt\n"',
      'file emptyfile.txt',
      'dir emptydir',
    ])

    fs = fs_local(tmp_dir)
    self.assertEqual( [
      ( 'emptyfile.txt', 0, 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', {} ),
      ( 'foo.txt', 8, 'b6a5ff9795209b3d64cb5c04d574515413f9fec7abde49d66b44de90d1e0db14', {} ),
    ], fs.list_dir('/', False) )
    
  @classmethod
  def _make_temp_content(clazz, items):
    return temp_content.write_items_to_temp_dir(items, delete = not clazz.DEBUG)
  
if __name__ == '__main__':
  unit_test.main()

#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from collections import namedtuple

from bes.files.match.bf_file_matcher import bf_file_matcher
from bes.files.resolve.bf_file_resolver import bf_file_resolver
from bes.files.resolve.bf_file_resolver_options import bf_file_resolver_options
from bes.fs.testing.temp_content import temp_content
from bes.system.log import logger

from bes.testing.unit_test import unit_test

class test_bf_file_resolver(unit_test):

  _log = logger('bf_file_resolver')
  
  @classmethod
  def _make_temp_content(clazz, items):
    return temp_content.write_items_to_temp_dir(items, delete = not clazz.DEBUG)

  _resolve_result = namedtuple('_resolve_result', 'tmp_dir, entries, relative_filenames, absolute_filenames, sorted_relative_filenames, sorted_absolute_filenames, stats')
  def _resolve(self, items, **options):
    resolver_options = bf_file_resolver_options(**options)
    tmp_dir = self._make_temp_content(items)
    f = bf_file_resolver(options = resolver_options)
    entries = f.resolve(tmp_dir)

    relative_filenames = entries.relative_filenames(False)
    absolute_filenames = entries.absolute_filenames(False)

    sorted_relative_filenames = entries.relative_filenames(True)
    sorted_absolute_filenames = entries.absolute_filenames(True)
    return self._resolve_result(tmp_dir,
                                entries,
                                relative_filenames,
                                absolute_filenames,
                                sorted_relative_filenames,
                                sorted_absolute_filenames,
                                None)
  
  def test_resolve_with_no_options(self):
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
    ], self._resolve(content).sorted_relative_filenames )
    
if __name__ == '__main__':
  unit_test.main()

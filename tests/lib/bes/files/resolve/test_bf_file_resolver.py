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

  _resolve_result = namedtuple('_resolve_result', 'tmp_dir, entries, entries_json, relative_filenames, absolute_filenames, sorted_relative_filenames, sorted_absolute_filenames, stats')
  def _resolve(self, items, where, **options):
    resolver_options = bf_file_resolver_options(**options)
    tmp_dir = self._make_temp_content(items)
    f = bf_file_resolver(options = resolver_options)
    abs_where = [ path.join(tmp_dir, next_where) for next_where in where ]
    print(abs_where)
    entries = f.resolve(abs_where)

    relative_filenames = entries.relative_filenames(False)
    absolute_filenames = entries.absolute_filenames(False)

    sorted_relative_filenames = entries.relative_filenames(True)
    sorted_absolute_filenames = entries.absolute_filenames(True)

    replacements = {
      tmp_dir: '${tmp_dir}',
    }
    entries_json = entries.to_json(replacements = replacements)
    return self._resolve_result(tmp_dir,
                                entries,
                                entries_json,
                                relative_filenames,
                                absolute_filenames,
                                sorted_relative_filenames,
                                sorted_absolute_filenames,
                                None)
  
  def test_resolve_with_no_options(self):
    content = [
      'file kiwi/foo.txt "foo.txt\n"',
      'file kiwi/subdir/bar.txt "bar.txt\n"',
      'file kiwi/subdir/subberdir/baz.txt "baz.txt\n"',
      'file kiwi/emptyfile.txt',
      'dir kiwi/emptydir',
    ]
    r = self._resolve(content, [ 'kiwi' ])

    self.assert_json_equal( '''
[
  {
    "filename": "emptyfile.txt",
    "root_dir": "${tmp_dir}/kiwi"
  },
  {
    "filename": "foo.txt",
    "root_dir": "${tmp_dir}/kiwi"
  },
  {
    "filename": "subdir/bar.txt",
    "root_dir": "${tmp_dir}/kiwi"
  },
  {
    "filename": "subdir/subberdir/baz.txt",
    "root_dir": "${tmp_dir}/kiwi"
  }
]
''', r.entries_json )

  def test_resolve_one_file(self):
    content = [
      'file kiwi/foo.txt "foo.txt\n"',
      'file kiwi/subdir/bar.txt "bar.txt\n"',
      'file kiwi/subdir/subberdir/baz.txt "baz.txt\n"',
      'file kiwi/emptyfile.txt',
      'dir kiwi/emptydir',
    ]
    r = self._resolve(content, [ 'kiwi/foo.txt' ])
    self.assert_json_equal( '''
[
  {
    "filename": "${tmp_dir}/kiwi/foo.txt",
    "root_dir": null
  }
]
''', r.entries_json )

  def test_resolve_two_files(self):
    content = [
      'file kiwi/foo.txt "foo.txt\n"',
      'file kiwi/subdir/bar.txt "bar.txt\n"',
      'file kiwi/subdir/subberdir/baz.txt "baz.txt\n"',
      'file kiwi/emptyfile.txt',
      'dir kiwi/emptydir',
    ]
    r = self._resolve(content, [ 'kiwi/foo.txt', 'kiwi/subdir/subberdir/baz.txt' ])
    self.assert_json_equal( '''
[
  {
    "filename": "${tmp_dir}/kiwi/foo.txt",
    "root_dir": null
  },
  {
    "filename": "${tmp_dir}/kiwi/subdir/subberdir/baz.txt",
    "root_dir": null
  }
]
''', r.entries_json )

  def test_resolve_one_file_and_one_dir(self):
    content = [
      'file kiwi/foo.txt "foo.txt\n"',
      'file kiwi/subdir/bar.txt "bar.txt\n"',
      'file kiwi/subdir/subberdir/baz.txt "baz.txt\n"',
      'file kiwi/emptyfile.txt',
      'dir kiwi/emptydir',
    ]
    r = self._resolve(content, [ 'kiwi/foo.txt', 'kiwi/subdir' ])

    self.assert_json_equal( '''
[
  {
    "filename": "${tmp_dir}/kiwi/foo.txt",
    "root_dir": null
  },
  {
    "filename": "bar.txt",
    "root_dir": "${tmp_dir}/kiwi/subdir"
  },
  {
    "filename": "subberdir/baz.txt",
    "root_dir": "${tmp_dir}/kiwi/subdir"
  }
]
''', r.entries_json )

  def test_resolve_two_dirs(self):
    content = [
      'file kiwi/foo.txt "foo.txt\n"',
      'file kiwi/subdir/bar.txt "bar.txt\n"',
      'file kiwi/subdir/subberdir/baz.txt "baz.txt\n"',
      'file kiwi/emptyfile.txt',
      'dir kiwi/emptydir',
      'file lemon/bar2.txt "bar2.txt\n"',
      'file lemon/subdir/bar3.txt "bar3.txt\n"',
    ]
    r = self._resolve(content, [ 'kiwi/subdir', 'lemon/subdir' ])

    self.assert_json_equal( '''
[
  {
    "filename": "bar.txt",
    "root_dir": "${tmp_dir}/kiwi/subdir"
  },
  {
    "filename": "subberdir/baz.txt",
    "root_dir": "${tmp_dir}/kiwi/subdir"
  },
  {
    "filename": "bar3.txt",
    "root_dir": "${tmp_dir}/lemon/subdir"
  }
]
''', r.entries_json )
    
if __name__ == '__main__':
  unit_test.main()

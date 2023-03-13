#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.files.match.bfile_match import bfile_match
from bes.files.find.bfile_finder import bfile_finder
from bes.files.find.bfile_finder_options import bfile_finder_options
from bes.files.bfile_entry import bfile_entry
from bes.files.bfile_entry_list import bfile_entry_list
from bes.fs.testing.temp_content import temp_content

from bes.testing.unit_test import unit_test

class test_bfile_finder(unit_test):

  @classmethod
  def _make_temp_content(clazz, items):
    return temp_content.write_items_to_temp_dir(items, delete = not clazz.DEBUG)

  def test_find_with_no_options(self):
    content = [
      'file foo.txt "foo.txt\n"',
      'file subdir/bar.txt "bar.txt\n"',
      'file subdir/subberdir/baz.txt "baz.txt\n"',
      'file emptyfile.txt',
      'dir emptydir',
    ]
    self.assert_filename_list_equal( [
      'foo.txt',
      'emptyfile.txt',
      'subdir',
      'emptydir',
      'subdir/bar.txt',
      'subdir/subberdir',
      'subdir/subberdir/baz.txt'
    ], self._find(content).filenames )

  def test_find_with_files_only(self):
    content = [
      'file foo.txt "foo.txt\n"',
      'file subdir/bar.txt "bar.txt\n"',
      'file subdir/subberdir/baz.txt "baz.txt\n"',
      'file emptyfile.txt',
      'dir emptydir',
    ]
    self.assert_filename_list_equal( [
      'foo.txt',
      'emptyfile.txt',
      'subdir/bar.txt',
      'subdir/subberdir/baz.txt'
    ], self._find(content, file_type = 'file').filenames )

  def test_find_with_dirs_only(self):
    content = [
      'file foo.txt "foo.txt\n"',
      'file subdir/bar.txt "bar.txt\n"',
      'file subdir/subberdir/baz.txt "baz.txt\n"',
      'file emptyfile.txt',
      'dir emptydir',
    ]
    self.assert_filename_list_equal( [
      'subdir',
      'emptydir',
      'subdir/subberdir',
    ], self._find(content, file_type = 'dir').filenames )
    
  _find_result = namedtuple('_find_result', 'tmp_dir, entries, filenames')
  def _find(self, items, **options):
    ff_options = bfile_finder_options(**options)
    tmp_dir = self._make_temp_content(items)
    f = bfile_finder(options = ff_options)
    entries = f.find(tmp_dir)
    return self._find_result(tmp_dir, entries, entries.filenames())

  '''
  def _match(self, match, filename, **options):
    entry = bfile_entry(filename)
    options = bfile_filename_matcher_options(**options_args)
    return match.match(entry)
                                     
  def test_match_fnmatch_one_matcher_any(self):
    m = bfile_match()
    m.add_matcher_fnmatch('*.py')
    self.assertEqual( True, m.match(bfile_entry('kiwi.py')) )
    self.assertEqual( False, m.match(bfile_entry('KIWI.PY')) )
    self.assertEqual( True, m.match(bfile_entry('/tmp/x/lemon.py')) )

  def test_match_fnmatch_two_matchers_all(self):
    m = bfile_match()
    m.add_matcher_fnmatch('*.py')
    m.add_matcher_fnmatch('k*')

    self.assertEqual( True, m.match(bfile_entry('kiwi.py'), match_type = 'ALL') )
    self.assertEqual( False, m.match(bfile_entry('lemon.py'), match_type = 'ALL') )

  def test_match_fnmatch_two_matchers_any(self):
    m = bfile_match()
    m.add_matcher_fnmatch('*.py')
    m.add_matcher_fnmatch('k*')

    self.assertEqual( True, m.match(bfile_entry('kiwi.py'), match_type = 'ANY') )
    self.assertEqual( True, m.match(bfile_entry('lemon.py'), match_type = 'ANY') )

  def test_match_fnmatch_one_matcher_any(self):
    m = bfile_match()
    m.add_matcher_fnmatch('*.py')
    self.assertEqual( True, m.match(bfile_entry('kiwi.py')) )
    self.assertEqual( False, m.match(bfile_entry('KIWI.PY')) )
    self.assertEqual( True, m.match(bfile_entry('/tmp/x/lemon.py')) )
    
  def test_match_entries_fnmatch_one_matcher_any(self):
    patterns = [
      '*.txt',
      '*.pdf',
    ]
    filenames = [
      'notes.txt',
      'report.pdf',
      'caca.jpg',
      'vaca.png',
      '/foo/bar/vaca.txt',
    ]
    expected = [
      'notes.txt',
      'report.pdf',
      '/foo/bar/vaca.txt',
    ]
    m = bfile_match()
    m.add_matcher_fnmatch(patterns)
    self.assertEqual( bfile_entry_list(expected), m.match_entries(filenames) )
'''
  
if __name__ == '__main__':
  unit_test.main()

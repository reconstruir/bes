#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.testing.unit_test import unit_test
from bes.files.ignore.bf_file_ignore import bf_file_ignore
from bes.files.bf_entry import bf_entry
from bes.fs.testing.temp_content import temp_content

class _bf_file_ignore_tester(object):

  def __init__(self, content, debug):
    self._debug = debug
    self._tmp_dir = self._make_temp_content(content)
    self._file_ignore = bf_file_ignore('.testing_test_ignore')

  @property
  def tmp_dir(self):
    return self._tmp_dir
  
  def _make_temp_content(self, items):
    return temp_content.write_items_to_temp_dir(items, delete = not self._debug)

  def _find_ignore_files(self, filename):
    entry = bf_entry(path.join(self._tmp_dir, filename))
    return self._file_ignore._find_ignore_files(entry, self._tmp_dir)

  def should_ignore(self, filename, ignore_missing_files = True):
    entry = bf_entry(path.join(self._tmp_dir, filename))
    return self._file_ignore.should_ignore(entry,
                                           self._tmp_dir,
                                           ignore_missing_files = ignore_missing_files)
    
class test_bf_file_ignore(unit_test):

  @classmethod
  def _make_temp_content(clazz, items):
    return temp_content.write_items_to_temp_dir(items, delete = not clazz.DEBUG)
  
  def _call_should_ignore(self, tmp_content_dir, ignore_filename, entry_fragment):
    fi = bf_file_ignore(ignore_filename)
    entry_path = path.join(tmp_content_dir, entry_fragment)
    entry = bf_entry(entry_path)
    return fi.should_ignore(entry)
    
  def test_should_ignore_basic(self):
    content = [
      'file a/b/c/.testing_test_ignore "d2\n\n" 644',
      'file a/b/c/d2/never.txt "this is never.txt\n" 644',
      'file a/b/c/d/bar.ttt "this is bar.ttt\n" 644',
      'file a/b/c/d/.testing_test_ignore "*.ttt\n" 644',
      'file a/b/c/d/foo.txt "this is foo.bar\n" 644',
    ]
    t = _bf_file_ignore_tester(content, self.DEBUG)
    self.assertEqual( True, t.should_ignore('something_not_there.txt') )
    self.assertEqual( False, t.should_ignore('a/b/c/d/foo.txt') )
    self.assertEqual( True, t.should_ignore('a/b/c/d/bar.ttt') )
    self.assertEqual( True, t.should_ignore('a/b/c/d2/never.txt') )

  def test_should_ignore_always_false(self):
    content = [
      'file a/b/c/.testing_test_ignore "d2\n\n" 644',
      'file a/b/c/d2/never.txt "this is never.txt\n" 644',
      'file a/b/c/d/bar.ttt "this is bar.ttt\n" 644',
      'file a/b/c/d/.testing_test_ignore "*.ttt\n" 644',
      'file a/b/c/d/foo.txt "this is foo.bar\n" 644',
    ]
    t = _bf_file_ignore_tester(content, self.DEBUG)
    self.assertEqual( False, t.should_ignore('a/b/c/d/foo.txt') )
    self.assertEqual( True, t.should_ignore('a/b/c/d/bar.ttt') )
    self.assertEqual( True, t.should_ignore('a/b/c/d2/never.txt') )
    
  def test__find_ignore_files_one_file(self):
    content = [
      'file fruit/kiwi.fruit',
      'file fruit/lemon.fruit',
      'file fruit/strawberry.fruit',
      'file fruit/blueberry.fruit',
      'file cheese/brie.cheese',
      'file cheese/cheddar.cheese',
      'file cheese/.testing_test_ignore "cheddar.cheese\n" 644',
    ]
    t = _bf_file_ignore_tester(content, self.DEBUG)
    self.assertEqual( [
      f'{t.tmp_dir}/cheese/.testing_test_ignore',
    ], t._find_ignore_files('cheese/cheddar.cheese') )

  def test__find_ignore_files_two_files(self):
    content = [
      'file fruit/kiwi.fruit',
      'file fruit/lemon.fruit',
      'file fruit/strawberry.fruit',
      'file fruit/blueberry.fruit',
      'file cheese/brie.cheese',
      'file cheese/cheddar.cheese',
      'file cheese/.testing_test_ignore "cheddar.cheese\n" 644',
      'file .testing_test_ignore "brie.cheese\n" 644',
    ]
    t = _bf_file_ignore_tester(content, self.DEBUG)
    self.assertEqual( [
      f'{t.tmp_dir}/cheese/.testing_test_ignore',
      f'{t.tmp_dir}/.testing_test_ignore',
    ], t._find_ignore_files('cheese/cheddar.cheese') )
                      
if __name__ == '__main__':
  unit_test.main()

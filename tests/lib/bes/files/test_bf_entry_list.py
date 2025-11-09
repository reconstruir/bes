#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.files.bf_entry import bf_entry
from bes.files.bf_entry_list import bf_entry_list
from bes.files.find.bf_file_finder import bf_file_finder
from bes.testing.unit_test import unit_test
from bes.testing.unit_test_function_skip import unit_test_function_skip

from bes.fs.testing.temp_content import temp_content

class _bf_entry_list_tester(object):

  def __init__(self, content, where = None):
    self._tmp_dir = self._make_temp_content(content)
    if where:
      find_where = [ path.join(self._tmp_dir, nw) for nw in where ]
    else:
      find_where = self._tmp_dir
    self._find_result = bf_file_finder.find_with_options(find_where)

  @property
  def tmp_dir(self):
    return self._tmp_dir

  @property
  def entries(self):
    return self._find_result.entries

  def make_entry(self, fragment):
    return bf_entry(path.join(self.tmp_dir, fragment))
  
  @classmethod
  def _make_temp_content(clazz, content):
    return temp_content.write_items_to_temp_dir(content, delete = not test_bf_entry_list.DEBUG)

class test_bf_entry_list(unit_test):
  
  def _make_test_entry(self, *args, **kargs):
    tmp = self.make_temp_file(*args, **kargs)
    return bf_entry(tmp)

  def _make_test_entry_dir(self, *args, **kargs):
    tmp = self.make_temp_dir(*args, **kargs)
    return bf_entry(tmp)

  def _make_test_entry_link(self, *args, **kargs):
    tmp1 = self.make_temp_file(*args, **kargs)
    tmp2 = self.make_temp_file(suffix = '-two')
    filesystem.remove(tmp2)
    os.symlink(tmp1, tmp2)
    return bf_entry(tmp2)

  def _make_tmp_dir(self):
    return self.make_temp_dir(prefix = 'test_bf_entry_list_', suffix = '.dir')

  def _make_test_entry_root_dir(self, root_dir, fragment, basename):
    filename = path.join(fragment, basename)
    return bf_entry(filename, root_dir = root_dir)
  
  def test_to_dict_list(self):
    t = _bf_entry_list_tester([
      'file fruit/kiwi.fruit "this is kiwi.fruit\n"',
      'file cheese/brie.cheese "this is brie.cheese\n"',
    ])
    self.assertEqual( [
      {
        'filename': self.native_filename('cheese/brie.cheese'),
        'root_dir': f'{t.tmp_dir}',
      },
      {
        'filename': self.native_filename('fruit/kiwi.fruit'),
        'root_dir': f'{t.tmp_dir}',
      },
    ], t.entries.to_dict_list() )

  def test_to_json(self):
    t = _bf_entry_list_tester([
      'file fruit/kiwi.fruit "this is kiwi.fruit\n"',
      'file cheese/brie.cheese "this is brie.cheese\n"',
    ])
    self.assert_json_equal( '''
[
  {
    "filename": "cheese/brie.cheese",
    "root_dir": "${tmp_dir}"
  },
  {
    "filename": "fruit/kiwi.fruit",
    "root_dir": "${tmp_dir}"
  }
]
''', t.entries.to_json(replacements = { t.tmp_dir: '${tmp_dir}' }) )
  
  def test_filenames(self):
    t = _bf_entry_list_tester([
      'file fruit/kiwi.fruit "this is kiwi.fruit\n"',
      'file cheese/brie.cheese "this is brie.cheese\n"',
    ])
    self.assertEqual( [
      self.native_filename(f'{t.tmp_dir}/cheese/brie.cheese'),
      self.native_filename(f'{t.tmp_dir}/fruit/kiwi.fruit'),
    ], t.entries.filenames() )

  def test_relative_filenames(self):
    t = _bf_entry_list_tester([
      'file fruit/kiwi.fruit "this is kiwi.fruit\n"',
      'file cheese/brie.cheese "this is brie.cheese\n"',
    ])
    self.assertEqual( [
      self.native_filename(f'cheese/brie.cheese'),
      self.native_filename(f'fruit/kiwi.fruit'),
    ], t.entries.relative_filenames() )

  def test_absolute_filenames(self):
    t = _bf_entry_list_tester([
      'file fruit/kiwi.fruit "this is kiwi.fruit\n"',
      'file cheese/brie.cheese "this is brie.cheese\n"',
    ])
    self.assertEqual( [
      self.native_filename(f'{t.tmp_dir}/cheese/brie.cheese'),
      self.native_filename(f'{t.tmp_dir}/fruit/kiwi.fruit'),
    ], t.entries.filenames() )

  def test_basenames(self):
    t = _bf_entry_list_tester([
      'file fruit/kiwi.fruit "this is kiwi.fruit\n"',
      'file cheese/brie.cheese "this is brie.cheese\n"',
    ])
    self.assertEqual( [
      'brie.cheese',
      'kiwi.fruit',
    ], t.entries.basenames() )

  def test_root_dirs(self):
    t = _bf_entry_list_tester([
      'file foo/fruit/kiwi.fruit "this is kiwi.fruit\n"',
      'file foo/cheese/brie.cheese "this is brie.cheese\n"',
      'file bar/fruit/kiwi.fruit "this is kiwi.fruit\n"',
      'file bar/cheese/brie.cheese "this is brie.cheese\n"',
    ], where = [ 'foo', 'bar' ])
    print(t.entries.root_dirs())
    self.assertEqual( [
      path.join(t.tmp_dir, 'bar'),
      path.join(t.tmp_dir, 'bar'),
      path.join(t.tmp_dir, 'foo'),
      path.join(t.tmp_dir, 'foo'),
    ], t.entries.root_dirs() )

  def test_unique_root_dirs(self):
    t = _bf_entry_list_tester([
      'file foo/fruit/kiwi.fruit "this is kiwi.fruit\n"',
      'file foo/cheese/brie.cheese "this is brie.cheese\n"',
      'file bar/fruit/kiwi.fruit "this is kiwi.fruit\n"',
      'file bar/cheese/brie.cheese "this is brie.cheese\n"',
    ], where = [ 'foo', 'bar' ])
    self.assertEqual( [
      path.join(t.tmp_dir, 'bar'),
      path.join(t.tmp_dir, 'foo'),
    ], t.entries.unique_root_dirs() )

  def test_absolute_common_ancestor(self):
    t = _bf_entry_list_tester([
      'file foo/fruit/kiwi.fruit "this is kiwi.fruit\n"',
      'file foo/cheese/brie.cheese "this is brie.cheese\n"',
      'file bar/fruit/kiwi.fruit "this is kiwi.fruit\n"',
      'file bar/cheese/brie.cheese "this is brie.cheese\n"',
    ], where = [ 'foo', 'bar' ])
    self.assertEqual( t.tmp_dir, t.entries.absolute_common_ancestor() )

if __name__ == '__main__':
  unit_test.main()

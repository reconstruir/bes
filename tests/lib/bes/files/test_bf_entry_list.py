#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.files.bf_entry import bf_entry
from bes.files.bf_entry_list import bf_entry_list
from bes.files.find.bf_file_finder import  bf_file_finder
from bes.testing.unit_test import unit_test
from bes.testing.unit_test_function_skip import unit_test_function_skip

from bes.fs.testing.temp_content import temp_content

from _bes_unit_test_common.unit_test_media import unit_test_media
from _bes_unit_test_common.unit_test_media_files import unit_test_media_files

class _bf_entry_list_tester(object):

  def __init__(self, content):
    self._tmp_dir = self._make_temp_content(content)
    self._find_result = bf_file_finder.find_with_options(self._tmp_dir)

  @property
  def tmp_dir(self):
    return self._tmp_dir

  @property
  def entries(self):
    return self._find_result.entries
  
  @classmethod
  def _make_temp_content(clazz, content):
    return temp_content.write_items_to_temp_dir(content, delete = not test_bf_entry_list.DEBUG)

class test_bf_entry_list(unit_test, unit_test_media_files):
  
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
      'file fruits/kiwi.fruit "this is kiwi.fruit\n"',
      'file cheese/brie.cheese "this is brie.cheese\n"',
    ])
    self.assertEqual( [
      {
        'filename': 'cheese/brie.cheese',
        'root_dir': f'{t.tmp_dir}',
      },
      {
        'filename': 'fruits/kiwi.fruit',
        'root_dir': f'{t.tmp_dir}',
      },
    ], t.entries.to_dict_list() )

  def test_to_json(self):
    t = _bf_entry_list_tester([
      'file fruits/kiwi.fruit "this is kiwi.fruit\n"',
      'file cheese/brie.cheese "this is brie.cheese\n"',
    ])
    replacements = { t.tmp_dir: '${tmp_dir}' }
    actual_json = t.entries.to_json(replacements = replacements)
    self.assert_json_equal( '''
[
  {
    "filename": "cheese/brie.cheese",
    "root_dir": "${tmp_dir}"
  },
  {
    "filename": "fruits/kiwi.fruit",
    "root_dir": "${tmp_dir}"
  }
]
''', actual_json )

  def test_filenames(self):
    t = _bf_entry_list_tester([
      'file fruits/kiwi.fruit "this is kiwi.fruit\n"',
      'file cheese/brie.cheese "this is brie.cheese\n"',
    ])
    self.assertEqual( [
      f'{t.tmp_dir}/cheese/brie.cheese',
      f'{t.tmp_dir}/fruits/kiwi.fruit',
    ], t.entries.filenames() )

  def test_relative_filenames(self):
    t = _bf_entry_list_tester([
      'file fruits/kiwi.fruit "this is kiwi.fruit\n"',
      'file cheese/brie.cheese "this is brie.cheese\n"',
    ])
    self.assertEqual( [
      f'cheese/brie.cheese',
      f'fruits/kiwi.fruit',
    ], t.entries.relative_filenames() )
    
if __name__ == '__main__':
  unit_test.main()

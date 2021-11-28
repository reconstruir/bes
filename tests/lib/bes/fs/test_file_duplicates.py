#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from os import path

from bes.testing.unit_test import unit_test
from bes.fs.file_util import file_util
from bes.fs.file_find import file_find
from bes.fs.dir_util import dir_util
from bes.fs.file_duplicates import file_duplicates
from bes.common.string_util import string_util

from bes.fs.testing.temp_content import temp_content
  
class test_file_duplicates(unit_test):

  def test_find_duplicates(self):
    self.assertEqual( [
      ( '${_root}/a/lemon.txt', [
        '${_root}/a/lemon_dup.txt',
        '${_root}/b/lemon_dup2.txt',
      ] ),
    ], self._test([ 
      'file a/lemon.txt "this is lemon.txt" 644',
      'file a/kiwi.txt "this is kiwi.txt" 644',
      'file a/lemon_dup.txt "this is lemon.txt" 644',
      'file b/lemon_dup2.txt "this is lemon.txt" 644',
    ], [ 'a', 'b' ]) )

  def test_find_duplicates_order(self):
    self.assertEqual( [
      ( '${_root}/b/lemon_dup2.txt', [
        '${_root}/a/lemon.txt',
        '${_root}/a/lemon_dup.txt',
      ] ),
    ], self._test([ 
      'file a/lemon.txt "this is lemon.txt" 644',
      'file a/kiwi.txt "this is kiwi.txt" 644',
      'file a/lemon_dup.txt "this is lemon.txt" 644',
      'file b/lemon_dup2.txt "this is lemon.txt" 644',
    ], [ 'b', 'a' ]) )
    
  _extra_dir = namedtuple('_extra_dir', 'dir, label')
  _test_result = namedtuple('_test_result', 'tmp_dir, dups, files')
  def _test(self, items, dirs, extra_dirs_before = [], extra_dirs_after = []):
    tmp_root = temp_content.write_items_to_temp_dir(items)
    tmp_root_dirs = [ path.join(tmp_root, d) for d in dirs ]
    dirs_for_find_dups_before = [ d.dirname for d in extra_dirs_before ]
    dirs_for_find_dups_after = [ d.dirname for d in extra_dirs_after ]
    dirs_for_find_dups = dirs_for_find_dups_before + tmp_root_dirs + dirs_for_find_dups_after
    dups = file_duplicates.find_duplicates(dirs_for_find_dups)
    replacements = {
      tmp_root: '${_root}',
    }
    return self._hack_dup_item_list(dups, replacements)

  @classmethod
  def _hack_dup_item(clazz, dup_item, replacements):
    new_filename = string_util.replace(dup_item.filename, replacements)
    new_duplicates = []
    for dup in dup_item.duplicates:
      new_duplicates.append(string_util.replace(dup, replacements))
    return file_duplicates._dup_item(new_filename, new_duplicates)
    
  @classmethod
  def _hack_dup_item_list(clazz, dup_item_list, replacements):
    result = []
    for dup_item in dup_item_list:
      result.append(clazz._hack_dup_item(dup_item, replacements))
    return result
    
if __name__ == '__main__':
  unit_test.main()

#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from os import path

from bes.common.string_util import string_util
from bes.fs.dir_util import dir_util
from bes.fs.file_duplicates import file_duplicates
from bes.fs.file_find import file_find
from bes.fs.file_util import file_util
from bes.system.which import which
from bes.testing.unit_test import unit_test
from bes.testing.unit_test_function_skip import unit_test_function_skip
from abc import abstractmethod, ABCMeta
from bes.system.compat import with_metaclass

from bes.fs.testing.temp_content import temp_content

class _file_duplicate_tester_base(with_metaclass(ABCMeta, object)):

  _extra_dir = namedtuple('_extra_dir', 'dirname, label')
  _test_result = namedtuple('_test_result', 'tmp_dir, dups, files')

  def __init__(self, ut):
    self._ut = ut
  
  @abstractmethod
  def find_dups(self, dirs):
    raise NotImplemented('find_dups')
  
  def test(self, items, dirs, extra_dirs_before = [], extra_dirs_after = []):
    tmp_root = temp_content.write_items_to_temp_dir(items)
    tmp_root_dirs = [ path.join(tmp_root, d) for d in dirs ]
    dirs_for_find_dups_before = [ d.dirname for d in extra_dirs_before ]
    dirs_for_find_dups_after = [ d.dirname for d in extra_dirs_after ]
    dirs_for_find_dups = dirs_for_find_dups_before + tmp_root_dirs + dirs_for_find_dups_after
    tmp_checksum_dir = self._ut.make_temp_dir()
    tmp_checksum_db_filename = path.join(tmp_checksum_dir, 'db.sqlite')
    dups = file_duplicates.find_duplicates(dirs_for_find_dups,
                                           checksum_db_filename = tmp_checksum_db_filename)
    replacements = {
      tmp_root: '${_root}',
    }
    for extra_dir in extra_dirs_before + extra_dirs_after:
      assert extra_dir.dirname not in replacements
      replacements[extra_dir.dirname] = extra_dir.label
    return self._hack_dup_item_list(dups, replacements)

  def _hack_dup_item(self, dup_item, replacements):
    new_filename = string_util.replace(dup_item.filename, replacements)
    new_duplicates = []
    for dup in dup_item.duplicates:
      new_duplicates.append(string_util.replace(dup, replacements))
    new_filename = self._ut.xp_filename(new_filename)
    new_duplicates = self._ut.xp_filename_list(new_duplicates)
    return file_duplicates._dup_item(new_filename, new_duplicates)
    
  def _hack_dup_item_list(self, dup_item_list, replacements):
    result = []
    for dup_item in dup_item_list:
      result.append(self._hack_dup_item(dup_item, replacements))
    return result
  
class _file_duplicate_tester_object(_file_duplicate_tester_base):
  #@abstractmethod
  def find_dups(self, dirs):
    return file_duplicates.find_duplicates(dirs_for_find_dups)

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

  @unit_test_function_skip.skip_if_not_unix()
  def test_find_duplicates_no_write_permission(self):
    sh_exe = which.which('sh')
    bin_dir = path.dirname(sh_exe)
    tmp_dir = self.make_temp_dir()
    sh_exe_dup = path.join(tmp_dir, 'dupsh.exe')
    file_util.copy(sh_exe, sh_exe_dup)
    result = self._test([ 
    ], [], extra_dirs_before = [
      _file_duplicate_tester_object._extra_dir(bin_dir, '${_bin}'),
      _file_duplicate_tester_object._extra_dir(tmp_dir, '${_tmp}'),
    ] )
    self.assertTrue( file_duplicates._dup_item('${_bin}/sh', [ '${_tmp}/dupsh.exe']) in result )

  def _test(self, items, dirs, extra_dirs_before = [], extra_dirs_after = []):
    tester = _file_duplicate_tester_object(self)
    return tester.test(items,
                       dirs,
                       extra_dirs_before = extra_dirs_before,
                       extra_dirs_after = extra_dirs_after)
    
if __name__ == '__main__':
  unit_test.main()

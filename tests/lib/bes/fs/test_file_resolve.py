#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.fs.file_resolve import file_resolve
from bes.fs.testing.temp_content import temp_content

class test_file_resolve(unit_test):

  def test_resolve_dir(self):
    tmp_dir = self._make_temp_content()
    self.assertEqual( [
      ( '${where}', self.xp_path('cheese/hard/cheddar.cheese'), self.xp_path('${where}/cheese/hard/cheddar.cheese') ),
      ( '${where}', self.xp_path('cheese/soft/brie.cheese'), self.xp_path('${where}/cheese/soft/brie.cheese') ),
      ( '${where}', self.xp_path('fruit/kiwi.fruit'), self.xp_path('${where}/fruit/kiwi.fruit') ),
      ( '${where}', self.xp_path('fruit/orange.fruit'), self.xp_path('${where}/fruit/orange.fruit') ),
    ], self._munge_result(file_resolve.resolve_dir(tmp_dir)) )

  def test_resolve_dir_with_patterns(self):
    tmp_dir = self._make_temp_content()
    self.assertEqual( [
      ( '${where}', self.xp_path('cheese/hard/cheddar.cheese'), self.xp_path('${where}/cheese/hard/cheddar.cheese') ),
      ( '${where}', self.xp_path('cheese/soft/brie.cheese'), self.xp_path('${where}/cheese/soft/brie.cheese') ),
    ], self._munge_result(file_resolve.resolve_dir(tmp_dir, patterns = [ '*.cheese' ])) )

  def test_resolve_mixed_dirs_only(self):
    tmp_dir = self._make_temp_content()

    self.assertEqual( [
      ( '${where}', self.xp_path('cheese/hard/cheddar.cheese'), self.xp_path('${where}/cheese/hard/cheddar.cheese') ),
      ( '${where}', self.xp_path('cheese/soft/brie.cheese'), self.xp_path('${where}/cheese/soft/brie.cheese') ),
    ], self._munge_result(file_resolve.resolve_mixed(tmp_dir, [ 'cheese' ])) )

    self.assertEqual( [
      ( '${where}', self.xp_path('fruit/kiwi.fruit'), self.xp_path('${where}/fruit/kiwi.fruit') ),
      ( '${where}', self.xp_path('fruit/orange.fruit'), self.xp_path('${where}/fruit/orange.fruit') ),
    ], self._munge_result(file_resolve.resolve_mixed(tmp_dir, [ 'fruit' ])) )
    
    self.assertEqual( [
      ( '${where}', self.xp_path('cheese/hard/cheddar.cheese'), self.xp_path('${where}/cheese/hard/cheddar.cheese') ),
      ( '${where}', self.xp_path('cheese/soft/brie.cheese'), self.xp_path('${where}/cheese/soft/brie.cheese') ),
      ( '${where}', self.xp_path('fruit/kiwi.fruit'), self.xp_path('${where}/fruit/kiwi.fruit') ),
      ( '${where}', self.xp_path('fruit/orange.fruit'), self.xp_path('${where}/fruit/orange.fruit') ),
    ], self._munge_result(file_resolve.resolve_mixed(tmp_dir, [ 'cheese', 'fruit' ])) )
    
  def test_resolve_mixed_dirs_only_duplicates(self):
    tmp_dir = self._make_temp_content()

    self.assertEqual( [
      ( '${where}', self.xp_path('cheese/hard/cheddar.cheese'), self.xp_path('${where}/cheese/hard/cheddar.cheese') ),
      ( '${where}', self.xp_path('cheese/soft/brie.cheese'), self.xp_path('${where}/cheese/soft/brie.cheese') ),
    ], self._munge_result(file_resolve.resolve_mixed(tmp_dir, [ 'cheese', 'cheese' ])) )

  def test_resolve_mixed_dirs_and_files(self):
    tmp_dir = self._make_temp_content()

    self.assertEqual( [
      ( '${where}', self.xp_path('cheese/hard/cheddar.cheese'), self.xp_path('${where}/cheese/hard/cheddar.cheese') ),
      ( '${where}', self.xp_path('cheese/soft/brie.cheese'), self.xp_path('${where}/cheese/soft/brie.cheese') ),
      ( '${where}', self.xp_path('fruit/orange.fruit'), self.xp_path('${where}/fruit/orange.fruit') ),
    ], self._munge_result(file_resolve.resolve_mixed(tmp_dir, [ 'cheese', self.xp_path('fruit/orange.fruit') ])) )

  def test_resolve_mixed_dirs_only_with_patterns(self):
    tmp_dir = self._make_temp_content()

    self.assertEqual( [
      ( '${where}', self.xp_path('cheese/hard/cheddar.cheese'), self.xp_path('${where}/cheese/hard/cheddar.cheese') ),
      ( '${where}', self.xp_path('cheese/soft/brie.cheese'), self.xp_path('${where}/cheese/soft/brie.cheese') ),
    ], self._munge_result(file_resolve.resolve_mixed(tmp_dir, [ 'cheese', 'fruit' ], patterns = [ '*.cheese' ])) )
    
  def test_resolve_mixed_no_args(self):
    tmp_dir = self._make_temp_content()

    self.assertEqual( [
      ( '${where}', self.xp_path('cheese/hard/cheddar.cheese'), self.xp_path('${where}/cheese/hard/cheddar.cheese') ),
      ( '${where}', self.xp_path('cheese/soft/brie.cheese'), self.xp_path('${where}/cheese/soft/brie.cheese') ),
      ( '${where}', self.xp_path('fruit/kiwi.fruit'), self.xp_path('${where}/fruit/kiwi.fruit') ),
      ( '${where}', self.xp_path('fruit/orange.fruit'), self.xp_path('${where}/fruit/orange.fruit') ),
    ], self._munge_result(file_resolve.resolve_mixed(tmp_dir, [])) )
    
  def _make_temp_content(self):
    tmp_dir = self.make_temp_dir()
    items = [
      'file cheese/soft/brie.cheese "this is brie" 644',
      'file cheese/hard/cheddar.cheese "this is cheddar" 644',
      'file fruit/kiwi.fruit "this is kiwi" 644',
      'file fruit/orange.fruit "this is orange" 644',
    ]
    temp_content.write_items(items, tmp_dir)
    return tmp_dir
    
  @classmethod
  def _munge_result(clazz, result):
    return sorted([ clazz._munge_one_result(rf) for rf in result ])

  @classmethod
  def _munge_one_result(clazz, rf):
    where = '${where}'
    filename = rf.filename
    filename_abs = rf.filename_abs.replace(rf.where, where)
    return file_resolve.resolved_file(where,
                                      filename,
                                      filename_abs)
    
if __name__ == "__main__":
  unit_test.main()

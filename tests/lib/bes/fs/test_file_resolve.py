#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.fs.file_resolve import file_resolve
from bes.fs.testing.temp_content import temp_content

class test_file_resolve(unit_test):

  def test_resolve_dir(self):
    tmp_dir = self._make_temp_content()
    self.assertEqual( [
      ( '${where}', 'cheese/brie.cheese', '${where}/cheese/brie.cheese' ),
      ( '${where}', 'cheese/cheddar.cheese', '${where}/cheese/cheddar.cheese' ),
      ( '${where}', 'fruit/kiwi.fruit', '${where}/fruit/kiwi.fruit' ),
      ( '${where}', 'fruit/orange.fruit', '${where}/fruit/orange.fruit' ),
    ], self._munge_result(file_resolve.resolve_dir(tmp_dir)) )

  def test_resolve_dir_with_patterns(self):
    tmp_dir = self._make_temp_content()
    self.assertEqual( [
      ( '${where}', 'cheese/brie.cheese', '${where}/cheese/brie.cheese' ),
      ( '${where}', 'cheese/cheddar.cheese', '${where}/cheese/cheddar.cheese' ),
    ], self._munge_result(file_resolve.resolve_dir(tmp_dir, patterns = [ '*.cheese' ])) )

  def _make_temp_content(self):
    filenames = [
      'cheese/brie.cheese',
      'cheese/cheddar.cheese',
      'fruit/kiwi.fruit',
      'fruit/orange.fruit',
    ]
    tmp_dir = self.make_temp_dir()
    items = [
      'file cheese/brie.cheese "brie.cheese" 644',
      'file cheese/cheddar.cheese "cheddar.cheese" 644',
      'file fruit/kiwi.fruit "kiwi.fruit" 644',
      'file fruit/orange.fruit "orange.fruit" 644',
    ]
    temp_content.write_items(items, tmp_dir)
    return tmp_dir
    
  @classmethod
  def _munge_result(clazz, result):
    return [ clazz._munge_one_result(rf) for rf in result ]

  @classmethod
  def _munge_one_result(clazz, rf):
    where = '${where}'
    filename = rf.filename
    filename_abs = rf.filename_abs.replace(rf.where, where)
    return file_resolve.resolved_file(where, filename, filename_abs)
    
if __name__ == "__main__":
  unit_test.main()

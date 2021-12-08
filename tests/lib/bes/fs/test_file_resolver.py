#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.fs.file_resolver import file_resolver
from bes.fs.testing.temp_content import temp_content

class test_file_resolve(unit_test):

  def test_resolve_files_just_root_dir(self):
    self.assertEqual( [
      ( '${tmp_dir}', 'cheese.txt', '${tmp_dir}/cheese.txt', 0 ),
    ], self._test([
      'file cheese.txt "this is cheese.txt" 644',
      'file a/lemon.txt "this is lemon.txt" 644',
      'file b/kiwi.txt "this is kiwi.txt" 644',
      'file subdir/orange.txt "this is orange.txt" 644',
      'file subdir/apple.txt "this is apple.txt" 644',
    ], [ '${tmp_dir}' ], recursive = False) )

  def test_resolve_files_just_root_dir_recursive(self):
    self.assertEqual( [
      ( '${tmp_dir}', 'a/lemon.txt', '${tmp_dir}/a/lemon.txt', 0 ),
      ( '${tmp_dir}', 'b/kiwi.txt', '${tmp_dir}/b/kiwi.txt', 1 ),
      ( '${tmp_dir}', 'cheese.txt', '${tmp_dir}/cheese.txt', 2 ),
      ( '${tmp_dir}', 'subdir/apple.txt', '${tmp_dir}/subdir/apple.txt', 3 ),
      ( '${tmp_dir}', 'subdir/orange.txt', '${tmp_dir}/subdir/orange.txt', 4 ),
    ], self._test([
      'file cheese.txt "this is cheese.txt" 644',
      'file a/lemon.txt "this is lemon.txt" 644',
      'file b/kiwi.txt "this is kiwi.txt" 644',
      'file subdir/orange.txt "this is orange.txt" 644',
      'file subdir/apple.txt "this is apple.txt" 644',
    ], [ '${tmp_dir}' ], recursive = True) )

  def test_resolve_files_two_dirs(self):
    self.assertEqual( [
      ( '${tmp_dir}/a', 'lemon.txt', '${tmp_dir}/a/lemon.txt', 0 ),
      ( '${tmp_dir}/b', 'kiwi.txt', '${tmp_dir}/b/kiwi.txt', 1 ),
#      ( '${tmp_dir}', 'cheese.txt', '${tmp_dir}/cheese.txt', 2 ),
#      ( '${tmp_dir}', 'subdir/apple.txt', '${tmp_dir}/subdir/apple.txt', 3 ),
#      ( '${tmp_dir}', 'subdir/orange.txt', '${tmp_dir}/subdir/orange.txt', 4 ),
    ], self._test([
      'file cheese.txt "this is cheese.txt" 644',
      'file a/lemon.txt "this is lemon.txt" 644',
      'file b/kiwi.txt "this is kiwi.txt" 644',
      'file subdir/orange.txt "this is orange.txt" 644',
      'file subdir/apple.txt "this is apple.txt" 644',
    ], [ '${tmp_dir}/a', '${tmp_dir}/b' ], recursive = False) )
    
  def _test(self,
            items,
            files,
            recursive = True,
            match_patterns = None,
            match_type = None,
            match_basename = True,
            match_function = None,
            match_re = None):
    tmp_dir = self.make_temp_dir()
    temp_content.write_items(items, tmp_dir)
    files = [ f.replace('${tmp_dir}', tmp_dir) for f in files ]
    result = file_resolver.resolve_files(files,
                                         recursive = recursive,
                                         match_patterns = match_patterns,
                                         match_type = match_type,
                                         match_basename = match_basename,
                                         match_function = match_function,
                                         match_re = match_re)
    return [ self._fix_one_resolved_file(f, tmp_dir) for f in result ] 

  @classmethod
  def _fix_one_resolved_file(clazz, resolved_file, tmp_dir):
    if resolved_file.root_dir != None:
      new_root_dir = resolved_file.root_dir.replace(tmp_dir, '${tmp_dir}')
      new_root_dir = clazz.xp_filename(new_root_dir)
      
    else:
      new_root_dir = None
    new_filename_abs = resolved_file.filename_abs.replace(tmp_dir, '${tmp_dir}')
    return file_resolver._resolved_file(new_root_dir,
                                        clazz.xp_filename(resolved_file.filename),
                                        clazz.xp_filename(new_filename_abs),
                                        resolved_file.order)
  
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
    
if __name__ == "__main__":
  unit_test.main()
